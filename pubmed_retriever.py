
import json
import time
import requests
import xml.etree.ElementTree as ET
import re

PUBMED_BASE_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
)

PUBMED_OUTPUT_FILE = "pubmed_candidates.json"
MAX_RESULTS_PER_QUERY = 50
MAX_UNIQUE_PMIDS = 100
REQUEST_TIMEOUT = 30

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "do", "does", "did", "can", "could", "should",
    "would", "will", "may", "might", "must",
    "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "and", "or", "but", "if",
    "every", "each", "all", "any", "person",
    "people", "it", "this", "that", "these",
    "those", "be", "being", "been", "have",
    "has", "had", "directly", "indirectly",
    "consuming", "consume", "consumed",
    "causes", "cause", "causing", "caused",
    "grow", "growth", "grows", "growing",
    "increase", "increases", "increased",
    "increasing", "affect", "affects"
}


def generate_search_queries(user_claim):
    """
    Generate multiple PubMed search queries from one claim.
    """
    queries = [user_claim.strip()]

    words = re.findall(r"\b[a-zA-Z]+\b", user_claim.lower())

    keywords = [
        word for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]

    # Search using the remaining keywords.
    if keywords:
        queries.append(" ".join(keywords))

    # Build a broader search using the core concepts.
    core_terms = list(dict.fromkeys(keywords))

    if len(core_terms) >= 2:
        queries.append(" AND ".join(core_terms))

    # Remove duplicate queries.
    unique_queries = []
    seen = set()

    for query in queries:
        query = query.strip()
        key = query.lower()

        if query and key not in seen:
            unique_queries.append(query)
            seen.add(key)

    print("\nGenerated PubMed queries:")
    for query in unique_queries:
        print(" -", query)

    return unique_queries


def search_pubmed_query(query):
    """
    Search PubMed for one query and return its total count and PMIDs.
    """
    url = PUBMED_BASE_URL + "esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": MAX_RESULTS_PER_QUERY,
        "retmode": "json",
        "sort": "relevance"
    }

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    data = response.json()
    search_data = data.get("esearchresult", {})

    total_count = int(search_data.get("count", 0))
    pmids = search_data.get("idlist", [])

    return total_count, pmids


def search_pubmed(user_claim):
    """
    Search PubMed with several query variations.
    Combine results and remove duplicate PMIDs.
    """
    queries = generate_search_queries(user_claim)

    all_pmids = []
    seen_pmids = set()
    query_results = []

    for query in queries:
        print(f"\nSearching PubMed for: {query}")

        try:
            total_count, pmids = search_pubmed_query(query)

            print(f"Total matching records: {total_count}")
            print(f"PMIDs retrieved for this query: {len(pmids)}")

            query_results.append({
                "query": query,
                "total_matching_records": total_count,
                "pmids_retrieved": len(pmids)
            })

            # Preserve retrieval order while removing duplicates.
            for pmid in pmids:
                if pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    all_pmids.append(pmid)

                if len(all_pmids) >= MAX_UNIQUE_PMIDS:
                    break

        except (requests.RequestException, ValueError) as error:
            print(f"Search failed for '{query}': {error}")

            query_results.append({
                "query": query,
                "error": str(error)
            })

        if len(all_pmids) >= MAX_UNIQUE_PMIDS:
            print(
                f"\nReached limit of "
                f"{MAX_UNIQUE_PMIDS} unique PMIDs."
            )
            break

        time.sleep(0.4)

    print("\nPubMed search summary:")
    print(f"Queries attempted: {len(query_results)}")
    print(f"Unique PMIDs collected: {len(all_pmids)}")

    return all_pmids, query_results


def get_text(element):
    if element is None:
        return ""

    return " ".join("".join(element.itertext()).split())


def fetch_pubmed_articles(pmids):
    """
    Fetch article metadata and abstracts for the retrieved PMIDs.
    """
    if not pmids:
        return []

    url = PUBMED_BASE_URL + "efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        citation = article.find("./MedlineCitation")

        article_element = (
            citation.find("./Article")
            if citation is not None
            else None
        )

        pmid = get_text(
            citation.find("./PMID")
            if citation is not None
            else None
        )

        if not pmid:
            continue

        title = get_text(
            article_element.find("./ArticleTitle")
            if article_element is not None
            else None
        )

        journal = get_text(
            article_element.find("./Journal/Title")
            if article_element is not None
            else None
        )

        abstract_parts = []

        if article_element is not None:
            for abstract_part in article_element.findall(
                "./Abstract/AbstractText"
            ):
                part_text = get_text(abstract_part)

                if part_text:
                    label = abstract_part.attrib.get("Label")

                    if label:
                        abstract_parts.append(
                            f"{label}: {part_text}"
                        )
                    else:
                        abstract_parts.append(part_text)

        abstract = " ".join(abstract_parts)

        pub_date = ""

        if article_element is not None:
            date_element = article_element.find(
                "./Journal/JournalIssue/PubDate"
            )

            if date_element is not None:
                date_parts = []

                for tag in (
                    "Year", "Month", "Day", "MedlineDate"
                ):
                    value = get_text(date_element.find(tag))

                    if value:
                        date_parts.append(value)

                pub_date = " ".join(date_parts)

        doi = ""

        for identifier in article.findall(
            ".//PubmedData/ArticleIdList/ArticleId"
        ):
            if identifier.attrib.get("IdType") == "doi":
                doi = get_text(identifier)
                break

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "publication_date": pub_date,
            "doi": doi or None,
            "pubmed_url": (
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            )
        })

    return articles


def run_pubmed_retrieval(user_claim):
    """
    Run expanded PubMed searches, fetch articles, and save JSON.
    """
    print("\nStarting expanded PubMed retrieval...")

    try:
        pmids, query_results = search_pubmed(user_claim)

        articles = fetch_pubmed_articles(pmids)

        output = {
            "user_claim": user_claim,
            "source": "PubMed",
            "retrieval_method": (
                "Query expansion with duplicate PMID removal"
            ),
            "queries": query_results,
            "unique_candidate_pmids": len(pmids),
            "articles_fetched": len(articles),
            "articles": articles
        }

        with open(
            PUBMED_OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"\nUnique PMIDs collected: {len(pmids)}")
        print(f"Articles fetched: {len(articles)}")
        print(f"Output saved to: {PUBMED_OUTPUT_FILE}")

        if not articles:
            print(
                "No articles were fetched. Try broader search "
                "terms or check the network connection."
            )

    except (
        requests.RequestException,
        ValueError,
        ET.ParseError
    ) as error:
        print(f"PubMed retrieval error: {error}")

        with open(
            PUBMED_OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump({
                "user_claim": user_claim,
                "source": "PubMed",
                "error": str(error),
                "queries": [],
                "unique_candidate_pmids": 0,
                "articles_fetched": 0,
                "articles": []
            }, file, indent=4, ensure_ascii=False)

