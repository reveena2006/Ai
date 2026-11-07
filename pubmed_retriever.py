
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
    "increasing", "affect", "affects",
    # Conversational scaffolds & filler nouns
    "one", "two", "reason", "reasons", "factor", "factors",
    "thing", "things", "way", "ways", "lead", "leads", "leading",
    "really", "actually", "true", "false", "good", "bad",
    "help", "helps", "helping", "problem", "problems", "issue", "issues",
    "relate", "related", "relation", "means", "mean"
}

COMMON_SYNONYMS = {
    "late sleep": '("late bedtime" OR "sleep duration" OR "circadian")',
    "sleeping late": '("late bedtime" OR "sleep deprivation")',
    "sleep late": '("late bedtime" OR "sleep duration")',
    "lack of sleep": '("sleep deprivation" OR "short sleep duration")',
    "high sugar": '("hyperglycemia" OR "diabetes")',
    "belly fat": '("abdominal adiposity" OR "obesity")',
    "high bp": '("hypertension")',
}


QUESTION_STARTERS = [
    r"^is\s+it\s+true\s+that\s+",
    r"^do\s+", r"^does\s+", r"^did\s+",
    r"^can\s+", r"^could\s+", r"^should\s+",
    r"^would\s+", r"^will\s+", r"^is\s+",
    r"^are\s+", r"^was\s+", r"^were\s+",
    r"^why\s+does\s+", r"^why\s+do\s+",
    r"^how\s+does\s+", r"^what\s+causes\s+",
    r"^what\s+is\s+the\s+link\s+between\s+",
    r"^tell\s+me\s+if\s+"
]

FILLER_PATTERNS = [
    r"\bone\s+of\s+the\s+reasons?\s+(for|of|behind)\b",
    r"\bone\s+of\s+the\s+causes?\s+(of|for|behind)\b",
    r"\bone\s+of\s+the\s+factors?\s+(in|for|of)\b",
    r"\ba\s+major\s+factor\s+(in|for|of)\b",
    r"\ba\s+leading\s+cause\s+of\b",
    r"\ba\s+reason\s+for\b",
    r"\bthe\s+reason\s+for\b",
    r"\blead\s+to\b",
    r"\bleads\s+to\b",
    r"\bleading\s+to\b",
    r"\bresponsible\s+for\b",
]


def clean_conversational_claim(claim_text):
    """
    Remove question starters, conversational filler phrases, and punctuation.
    """
    text = claim_text.strip().lower()
    text = re.sub(r"[?!.,;]+$", "", text)
    for pattern in QUESTION_STARTERS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    for pattern in FILLER_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    return text.strip()


def generate_search_queries(user_claim):
    """
    Option A: Clean concepts passed unquoted to PubMed for native MeSH ATM translation.
    Removes conversational fluff ("do", "is it true that", "one of the reason") and
    passes space-separated clean terms without forced ANDs or quotes.
    """
    cleaned = clean_conversational_claim(user_claim)

    words = re.findall(r"\b[a-zA-Z]+\b", cleaned)
    keywords = [
        word for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]

    queries = []

    # 1. Primary Query: Unquoted clean concepts for PubMed Automatic Term Mapping (ATM)
    # PubMed natively expands unquoted terms into (Concept[MeSH Terms] OR Concept[All Fields])
    if keywords:
        queries.append(" ".join(keywords))

    # 2. Common colloquial-to-biomedical concept expansions (unquoted for ATM)
    for layman, medical in COMMON_SYNONYMS.items():
        if layman in cleaned:
            layman_words = set(layman.split())
            remaining = [w for w in keywords if w not in layman_words]
            if remaining:
                queries.append(f"{medical} {' '.join(remaining)}")
            else:
                queries.append(medical)

    # 3. Core concepts fallback (e.g. if >= 3 keywords, pair primary concepts)
    if len(keywords) >= 3:
        queries.append(f"{keywords[0]} {keywords[-1]}")

    # Fallback to verbatim claim if all filters returned empty
    if not queries:
        queries.append(user_claim.strip())

    # Remove duplicate queries while preserving order.
    unique_queries = []
    seen = set()

    for query in queries:
        query = query.strip()
        key = query.lower()

        if query and key not in seen:
            unique_queries.append(query)
            seen.add(key)

    print("\nGenerated PubMed queries (Option A: ATM-Optimized):")
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
    atm_translation = search_data.get("querytranslation", "")
    if atm_translation:
        print(f"   [PubMed ATM Translation]: {atm_translation}")

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

