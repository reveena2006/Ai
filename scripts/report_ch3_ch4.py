"""
Generates Chapter 3 (System Design) and Chapter 4 (Implementation)
for the AI-Assisted Health-Related Misinformation Verification System project report.
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_helpers import (
    add_p, add_heading_1, add_heading_2, add_heading_3,
    add_bullet_item, add_numbered_item, format_table, add_callout,
    add_figure_image
)

def build_chapter_3(doc):
    add_heading_1(doc, "CHAPTER 3 – SYSTEM DESIGN")

    add_heading_2(doc, "3.1 Introduction")
    add_p(
        doc,
        "System design is the foundational phase of software engineering where user and academic requirements are converted into a concrete, "
        "modular, and verifiable architectural specification. The design must establish the overall structural decomposition, module "
        "boundaries, inter-service data flows, database schemas, and decision-making logic. In healthcare verification systems, design "
        "rigor is particularly crucial: errors in evidence flow or uncontrolled generative behavior can directly compromise the truthfulness "
        "and safety of delivered health advice."
    )

    add_heading_2(doc, "3.2 Existing System and Its Limitations")
    add_p(
        doc,
        "Conventional approaches to health claim verification rely either on manual human fact-checking or basic keyword-based search "
        "interfaces. In the manual workflow, medical librarians or professional fact-checkers manually formulate complex Boolean search queries "
        "(e.g., '(ginger OR zingiber) AND (asthma OR bronchospasm) AND clinical trial'), read dozens of PDF publications, and manually synthesize "
        "a consensus statement. While human expertise ensures high clinical accuracy, manual fact-checking requires hours or days per claim and "
        "cannot scale to the hundreds of thousands of claims circulating across digital channels."
    )
    add_p(
        doc,
        "Conversely, existing automated search engines and simple fact-checking chatbots suffer from three major design vulnerabilities:"
    )
    add_bullet_item(doc, "Keyword Matching Fragility: Lexical search engines retrieve articles containing query keywords regardless of whether the article confirms or debunks the claim.", bold_prefix="1. Lexical Brittleness: ")
    add_bullet_item(doc, "Uncontrolled Generative Hallucination: Modern conversational LLMs generate fluent text that frequently hallucinates fabricated medical studies and non-existent PubMed citations.", bold_prefix="2. Generative Hallucination: ")
    add_bullet_item(doc, "Single-Source Vulnerability: Tools that rely solely on Wikipedia or journalistic fact-checks cannot evaluate novel clinical claims that have only appeared in primary academic literature.", bold_prefix="3. Knowledge Siloing: ")

    add_heading_2(doc, "3.3 Proposed System Architecture")
    add_p(
        doc,
        "To resolve these fundamental limitations, the proposed system adopts a deterministic, multi-stage, evidence-grounded architecture. "
        "The architecture is organized into five specialized functional layers, ensuring that information retrieval, neural ranking, stance "
        "inference, and decision adjudication operate as distinct, auditable components."
    )

    add_heading_2(doc, "3.4 System Requirements Specification")

    add_heading_3(doc, "3.4.1 Functional Requirements")
    add_p(
        doc,
        "Functional requirements define the core operational capabilities that the verification system must provide to users. Table 3.1 "
        "outlines the verified functional requirements implemented in the project codebase."
    )

    t_fr = doc.add_table(rows=7, cols=3)
    format_table(
        t_fr,
        [Inches(1.2), Inches(2.2), Inches(3.3)],
        ["Req. ID", "Functional Requirement", "Operational Description"],
        [
            ["FR-01", "Claim Ingestion", "Accepts free-form natural language health claims and validates input integrity."],
            ["FR-02", "Dual-Source Retrieval", "Dispatches automated search queries to Google Fact Check Tools API and NCBI PubMed."],
            ["FR-03", "Neural Document Re-Ranking", "Executes SBERT Bi-Encoder for fact-checks and MedCPT Cross-Encoder for PubMed abstracts."],
            ["FR-04", "Top-K Evidence Selection", "Filters and preserves the Top-10 most relevant candidate records per source stream."],
            ["FR-05", "Directional Stance Inference", "Computes NLI entailment, contradiction, and neutral distributions via DeBERTa-v3-large."],
            ["FR-06", "Deterministic Decision Engine", "Aggregates multi-source evidence tallies under a contradiction-precedent rule hierarchy."],
        ],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )

    p_cap_fr = doc.add_paragraph()
    p_cap_fr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_fr.paragraph_format.space_before = Pt(4)
    p_cap_fr.paragraph_format.space_after = Pt(12)
    r_cfr = p_cap_fr.add_run("Table 3.1: Functional Requirements Specification Matrix")
    r_cfr.font.name = "Times New Roman"
    r_cfr.font.size = Pt(10)
    r_cfr.bold = True

    add_heading_3(doc, "3.4.2 Non-Functional Requirements")
    add_bullet_item(doc, "Maintain an end-to-end processing latency under 15–20 seconds for standard queries running on CPU.", bold_prefix="Performance & Latency: ")
    add_bullet_item(doc, "Every claim assessment must link directly to immutable external sources (PMID, DOI, fact-check URLs). Zero ungrounded text generation.", bold_prefix="Explainability & Provenance: ")
    add_bullet_item(doc, "The decision engine must prioritize refuting evidence to prevent false reassurance on hazardous health assertions.", bold_prefix="Clinical Safety Precedence: ")
    add_bullet_item(doc, "Native pure-Python fallbacks must prevent application crashes if optional machine learning packages or network endpoints fail.", bold_prefix="Fault Tolerance & Resilience: ")

    add_heading_2(doc, "3.5 System Architecture Diagram & Layers")
    add_p(
        doc,
        "Figure 3.1 illustrates the overall multi-stage system architecture, detailing the progression of a health claim from ingestion "
        "through dual-source retrieval, neural ranking, inference, and final adjudication."
    )

    add_figure_image(doc, "fig3_1_architecture.png", "Figure 3.1: Overall Multi-Stage Verification System Architecture", width_inches=5.8)

    add_p(
        doc,
        "The architecture is organized into five cohesive layers:"
    )
    add_numbered_item(doc, "1", "Ingestion and Retrieval Layer: Ingests the user claim and fetches candidate documents from Google Fact Check and PubMed.", bold_prefix="Layer 1: ")
    add_numbered_item(doc, "2", "Neural Re-Ranking Layer: Applies SBERT (cosine similarity) and MedCPT (cross-attention) to extract the Top-10 candidates per stream.", bold_prefix="Layer 2: ")
    add_numbered_item(doc, "3", "Stance Inference Layer: Executes DeBERTa-v3-large to derive directional entailment, contradiction, and neutral probabilities.", bold_prefix="Layer 3: ")
    add_numbered_item(doc, "4", "Decision Adjudication Layer: Evaluates evidence tallies through deterministic rule hierarchies to determine the final verdict.", bold_prefix="Layer 4: ")
    add_numbered_item(doc, "5", "Presentation & Evaluation Layer: Serves the Streamlit web dashboard and executes quantitative performance evaluations.", bold_prefix="Layer 5: ")

    add_heading_2(doc, "3.6 Module Description")
    add_p(
        doc,
        "The software architecture decomposes the verification problem into eight verified modules:"
    )
    add_numbered_item(doc, "1", "Claim Input Module: Validates user strings, trims whitespace, and prepares normalized queries for search dispatching.", bold_prefix="Module 1: ")
    add_numbered_item(doc, "2", "Fact-Check Retrieval Module: Communicates with Google Fact Check Tools API, retrieving up to 100 candidate claim reviews.", bold_prefix="Module 2: ")
    add_numbered_item(doc, "3", "PubMed Retrieval Module: Formulates multi-query expansions, searches NCBI E-Utilities, deduplicates PMIDs (ceiling 100), and fetches XML abstracts.", bold_prefix="Module 3: ")
    add_numbered_item(doc, "4", "SBERT Ranking Module: Computes 384-dimensional dense embeddings for fact-checks and user claims, sorting by cosine similarity.", bold_prefix="Module 4: ")
    add_numbered_item(doc, "5", "MedCPT Cross-Encoder Ranking Module: Performs deep cross-attention between claims and PubMed abstracts, ranking by biomedical relevance.", bold_prefix="Module 5: ")
    add_numbered_item(doc, "6", "NLI Stance Classification Module: Pairs ranked evidence with the claim under an uncontaminated premise to compute stance vectors.", bold_prefix="Module 6: ")
    add_numbered_item(doc, "7", "Decision Engine Module: Enforces contradiction-precedent aggregation rules to output canonical verdicts, confidence scores, and reasoning traces.", bold_prefix="Module 7: ")
    add_numbered_item(doc, "8", "Result Presentation & Evaluation Module: Implements the Streamlit UI, renders evidence cards with PMIDs, and executes evaluation metrics.", bold_prefix="Module 8: ")

    add_heading_2(doc, "3.7 Data Flow Diagram (DFD)")
    add_p(
        doc,
        "Figure 3.2 illustrates the Level 1 Data Flow Diagram (DFD) of the system, mapping data stores, external entities, and processes."
    )

    add_figure_image(doc, "fig3_2_dataflow.png", "Figure 3.2: Level 1 Data Flow Diagram (DFD) of System Processing", width_inches=5.8)

    add_heading_2(doc, "3.8 End-to-End System Workflow")
    add_p(
        doc,
        "The end-to-end execution sequence follows six strictly ordered stages:"
    )
    add_numbered_item(doc, "1", "User submits a health claim via the Streamlit web interface or command line.", bold_prefix="Stage 1 (Submission): ")
    add_numbered_item(doc, "2", "Module 1 dispatches parallel retrieval requests to the Google Fact Check API and NCBI PubMed E-Utilities.", bold_prefix="Stage 2 (Retrieval): ")
    add_numbered_item(doc, "3", "Module 2 executes SBERT Bi-Encoder ranking on fact-checks and MedCPT Cross-Encoder ranking on PubMed abstracts, selecting Top-10 per stream.", bold_prefix="Stage 3 (Re-Ranking): ")
    add_numbered_item(doc, "4", "Module 3 pairs each Top-10 record with the claim and passes them through DeBERTa-v3-large to compute directional stance probabilities.", bold_prefix="Stage 4 (Inference): ")
    add_numbered_item(doc, "5", "Module 4 tallies the stance counts across both streams and evaluates contradiction-precedent decision rules to synthesize the final verdict.", bold_prefix="Stage 5 (Adjudication): ")
    add_numbered_item(doc, "6", "Module 5 renders the verdict banner, confidence score, transparent reasoning trace, and interactive evidence cards with active citation links.", bold_prefix="Stage 6 (Presentation): ")

    add_heading_2(doc, "3.9 Decision-Making Logic & Canonical Verdicts")
    add_p(
        doc,
        "The decision engine evaluates evidence tallies: total supporting evidence (E_total) and total contradicting evidence (C_total). "
        "Figure 3.6 illustrates the contradiction-precedent decision flowchart."
    )

    add_figure_image(doc, "fig3_6_decision.png", "Figure 3.6: Decision Engine Contradiction-Precedent Adjudication Flowchart", width_inches=5.2)

    add_p(
        doc,
        "The system classifies every evaluated claim into one of four mutually exclusive canonical verdict categories, as formally defined in Table 3.2."
    )

    t_v = doc.add_table(rows=5, cols=3)
    format_table(
        t_v,
        [Inches(1.8), Inches(1.8), Inches(3.1)],
        ["Canonical Verdict", "Activation Rule", "Clinical & Epistemic Interpretation"],
        [
            ["Potentially refuted", "C_total > E_total AND C_total >= 1\nOR Debunked Fact-Check Rating", "Primary biomedical research or certified fact-checkers actively contradict the assertion."],
            ["Potentially supported", "E_total > C_total AND E_total >= 1\nAND Zero Strong Contradiction", "Authoritative clinical evidence or fact-checking consensus validates the assertion."],
            ["Mixed evidence", "E_total >= 1 AND C_total >= 1\n(Conflicting Signals)", "Reputable scientific studies or fact-checkers report contradictory or divided clinical outcomes."],
            ["Insufficient evidence", "Total Evidence == 0 OR\nNeutral Dominance (N_total >> 0)", "Available biomedical literature is inconclusive, unrelated, or lacks statistically significant evidence."],
        ],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )

    p_cap_tv = doc.add_paragraph()
    p_cap_tv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_tv.paragraph_format.space_before = Pt(4)
    p_cap_tv.paragraph_format.space_after = Pt(12)
    r_ctv = p_cap_tv.add_run("Table 3.2: Canonical Verdict Category Definitions and Operational Semantics")
    r_ctv.font.name = "Times New Roman"
    r_ctv.font.size = Pt(10)
    r_ctv.bold = True

    add_heading_2(doc, "3.10 Use Case Diagram")
    add_p(
        doc,
        "Figure 3.3 presents the UML Use Case Diagram, illustrating the interactions between the everyday end user (the general public seeking health verification) and the application."
    )

    add_figure_image(doc, "fig3_3_usecase.png", "Figure 3.3: Use Case Diagram for Verification Application & Public User Workflows", width_inches=5.4)

    add_heading_2(doc, "3.11 Design Considerations & Engineering Constraints")
    add_bullet_item(doc, "Modularity & Loose Coupling: Each module communicates through standardized JSON interfaces, allowing rankers or classifiers to be updated without redesigning the UI.", bold_prefix="1. Modularity: ")
    add_bullet_item(doc, "Scientific Provenance: Every piece of evidence presented retains its PMID, DOI, journal title, and source URL.", bold_prefix="2. Provenance: ")
    add_bullet_item(doc, "Dual-Source Triangulation: Combines journalistic fact-checking for internet myths with PubMed for clinical authority.", bold_prefix="3. Triangulation: ")
    add_bullet_item(doc, "Non-Generative Truth Adjudication: Prevents LLM hallucinations by using deterministic rules over calibrated NLI probabilities.", bold_prefix="4. Safety: ")
    add_bullet_item(doc, "Graceful Degradation: Native pure-Python fallbacks ensure the system remains operational even if optional libraries fail.", bold_prefix="5. Resilience: ")

    add_heading_2(doc, "3.12 Chapter Summary")
    add_p(
        doc,
        "This chapter detailed the comprehensive system design of the AI-Assisted Health-Related Misinformation Verification System. "
        "It specified the functional requirements, architectural layers, DFDs, use case models, two-tier ranking architecture, "
        "NLI stance analysis flow, and the contradiction-precedent decision logic. This establishes the structural blueprint for "
        "the implementation described in Chapter 4."
    )

def build_chapter_4(doc):
    add_heading_1(doc, "CHAPTER 4 – IMPLEMENTATION")

    add_heading_2(doc, "4.1 Introduction")
    add_p(
        doc,
        "Implementation is the stage where architectural specifications, neural models, and decision algorithms are translated into "
        "executable, production-ready software. This chapter details the technical implementation of the AI-Assisted Health-Related "
        "Misinformation Verification System, covering programming languages, libraries, API connectors, ranking implementations, NLI inference, "
        "user interface design, error handling, and testing procedures based directly on the project codebase."
    )

    add_heading_2(doc, "4.2 Technologies and Software Libraries Used")
    add_p(
        doc,
        "The project is implemented in Python 3.12, leveraging specialized machine learning frameworks, NLP libraries, and web presentation "
        "tools. Table 4.1 documents the core software libraries and their concrete applications in the codebase."
    )

    t_tech = doc.add_table(rows=8, cols=4)
    format_table(
        t_tech,
        [Inches(1.5), Inches(1.1), Inches(2.2), Inches(1.9)],
        ["Library / Technology", "Version", "Purpose in Project", "Primary Source File"],
        [
            ["Python", "3.12.10", "Core programming runtime", "All project modules"],
            ["PyTorch", "2.14.1", "Deep learning tensor computation", "nli_classifier.py, run_both_rankers.py"],
            ["Hugging Face Transformers", "5.19.0", "Transformer model loading & tokenization", "nli_classifier.py, run_both_rankers.py"],
            ["Sentence-Transformers", "6.1.0", "Dense sentence embedding generation", "sbert_ranker.py"],
            ["Streamlit", "1.66.0", "Interactive web application dashboard", "app.py"],
            ["scikit-learn", "1.9.1", "Evaluation metrics calculation", "evaluation_metrics.py"],
            ["Requests / Urllib3", "2.34.2", "HTTP communication with PubMed & Google APIs", "factcheck_retriever.py, pubmed_retriever.py"],
        ],
        [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )

    p_cap_tech = doc.add_paragraph()
    p_cap_tech.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_tech.paragraph_format.space_before = Pt(4)
    p_cap_tech.paragraph_format.space_after = Pt(12)
    r_ctech = p_cap_tech.add_run("Table 4.1: Software Libraries, Frameworks, and Core Dependencies")
    r_ctech.font.name = "Times New Roman"
    r_ctech.font.size = Pt(10)
    r_ctech.bold = True

    add_heading_2(doc, "4.3 Development Environment and Hardware Setup")
    add_p(
        doc,
        "Development and evaluation were conducted on a 64-bit Windows workstation equipped with Python 3.12 virtual environments (.venv312). "
        "To ensure accessibility for students, clinical staff, and researchers without expensive GPU servers, all models—including MedCPT "
        "and DeBERTa-v3-large—were optimized to execute efficiently on modern multi-core x86_64 CPUs using optimized PyTorch matrix operations "
        "and single-batch inference."
    )

    add_heading_2(doc, "4.4 Claim Input and Preprocessing")
    add_p(
        doc,
        "The claim entry point is managed by app.py and main.py. Submitted claims are stripped of leading/trailing whitespace, validated "
        "against empty string injection, and sanitized against HTML/XSS formatting. The sanitized string serves as the common query key "
        "for both retrieval streams."
    )

    add_heading_2(doc, "4.5 Google Fact Check Tools API Integration")
    add_p(
        doc,
        "Fact-check retrieval is implemented in factcheck_retriever.py and integrated into app.py. The service queries the endpoint "
        "'https://factchecktools.googleapis.com/v1alpha1/claims:search' passing the user claim as the query parameter. The API returns "
        "structured claim reviews containing claim date, claimant identity, fact-checking publisher name, review rating, and review URL. "
        "The system requests up to 100 candidate claim reviews per query. Candidates are parsed and cached locally in factcheck_results.json."
    )

    add_heading_2(doc, "4.6 PubMed Biomedical Retrieval Subsystem")
    add_p(
        doc,
        "PubMed retrieval is implemented in pubmed_retriever.py. Because clinical queries often fail under exact string matching, the module "
        "implements multi-query expansion, issuing three parallel searches via NCBI E-Utilities esearch: (1) verbatim user claim, (2) biomedical "
        "entities, and (3) clinical conjunctions (disease + outcome). Each search requests retmax = 50 candidate PMIDs."
    )
    add_p(
        doc,
        "To prevent duplicate processing and comply with NCBI throughput constraints, a hash-set deduplication filter merges identical PMIDs "
        "and enforces a strict global ceiling of 100 unique PMIDs. All unique PMIDs are fetched in a single XML batch call via efetch. "
        "Table 4.2 summarizes the retrieval limits and deduplication rules."
    )

    t_ret = doc.add_table(rows=5, cols=4)
    format_table(
        t_ret,
        [Inches(1.8), Inches(1.2), Inches(2.2), Inches(1.5)],
        ["Retrieval Parameter", "Configured Limit", "Engineering Justification", "Observed Latency"],
        [
            ["Google Fact Check Limit", "100 records", "Captures all relevant global journalistic claim reviews", "< 1.5 seconds"],
            ["PubMed retmax per query", "50 PMIDs", "Biomedical IR studies show precision degrades beyond rank 50", "< 1.0 second"],
            ["PubMed Max Unique PMIDs", "100 PMIDs", "Fits single-batch XML efetch guidelines (<3s fetch time)", "< 2.5 seconds"],
            ["Top-K Evidence Selection", "Top-10 / source", "Sufficient clinical coverage without overwhelming NLI", "Instantaneous"],
        ],
        [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]
    )

    p_cap_ret = doc.add_paragraph()
    p_cap_ret.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_ret.paragraph_format.space_before = Pt(4)
    p_cap_ret.paragraph_format.space_after = Pt(12)
    r_cret = p_cap_ret.add_run("Table 4.2: System Retrieval Ceilings, Query Limits, and Deduplication Rules")
    r_cret.font.name = "Times New Roman"
    r_cret.font.size = Pt(10)
    r_cret.bold = True

    add_heading_2(doc, "4.7 SBERT Bi-Encoder Ranking Implementation")
    add_p(
        doc,
        "Implemented in sbert_ranker.py, the SBERT ranking engine loads sentence-transformers/all-MiniLM-L6-v2. The model maps the user "
        "claim and candidate fact-checking records into 384-dimensional dense vectors. Relevance is computed as normalized cosine similarity:"
    )
    add_p(
        doc,
        "Score_SBERT(q, d) = (u · v) / (||u|| * ||v||)",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        bold_prefix="Cosine Similarity Formula: "
    )
    add_p(
        doc,
        "Candidate fact-checks are sorted in descending order of similarity, and the Top-10 highest-scoring entries are preserved in "
        "top10_ranked_factchecks.json."
    )

    add_heading_2(doc, "4.8 MedCPT Cross-Encoder-Based PubMed Ranking")
    add_p(
        doc,
        "Implemented in run_both_rankers.py, the scientific literature ranking engine loads ncbi/MedCPT-Cross-Encoder. Unlike bi-encoders, "
        "MedCPT performs joint cross-attention across concatenated token sequences: '[CLS] Claim [SEP] Title + Abstract [SEP]'. "
        "Figure 3.4 contrasts the SBERT bi-encoder and MedCPT cross-encoder architectures."
    )

    add_figure_image(doc, "fig3_4_ranking.png", "Figure 3.4: Architecture Comparison: SBERT Bi-Encoder vs MedCPT Cross-Encoder", width_inches=5.8)

    add_p(
        doc,
        "MedCPT produces a single continuous relevance logit passed through a sigmoid function. The candidate PubMed articles are ordered "
        "by score, and the Top-10 articles are preserved in output/top10_ranked_articles.json."
    )

    add_heading_2(doc, "4.9 Natural Language Inference Stance Classifier")
    add_p(
        doc,
        "Implemented in nli_classifier.py, the inference engine loads cross-encoder/nli-deberta-v3-large. The model processes the paired "
        "sequence: Premise (retrieved document abstract) and Hypothesis (user health claim). Figure 3.5 illustrates the NLI stance "
        "classification process."
    )

    add_figure_image(doc, "fig3_5_nli.png", "Figure 3.5: Natural Language Inference (NLI) Stance Classification Architecture", width_inches=5.8)

    add_p(
        doc,
        "The model outputs three logits corresponding to entailment, contradiction, and neutral. Probabilities are derived via softmax:"
    )
    add_p(
        doc,
        "P(y = c | P, H) = exp(z_c) / sum_j(exp(z_j))",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        bold_prefix="Softmax Probability: "
    )
    add_p(
        doc,
        "The predicted stance label is selected via argmax, and the maximum probability is recorded as the confidence score. Crucially, "
        "our implementation enforces an uncontaminated premise formulation: the user claim is NEVER concatenated into the premise."
    )

    add_heading_2(doc, "4.10 Multi-Source Deterministic Decision Engine")
    add_p(
        doc,
        "Implemented in decision_engine.py, the decision engine synthesizes classified evidence from both streams. It tallies active supporting "
        "evidence (E_total) and active contradicting evidence (C_total). In accordance with clinical safety guidelines, it enforces contradiction "
        "precedence: if C_total > E_total and C_total >= 1, the verdict is assigned as 'Potentially refuted'. If E_total > C_total and E_total >= 1 "
        "with zero strong contradiction, the verdict is 'Potentially supported'. If both supporting and contradicting evidence exist (E_total >= 1 "
        "and C_total >= 1), the verdict is 'Mixed evidence'. If zero relevant evidence or only neutral context exists, the verdict is 'Insufficient evidence'."
    )

    add_heading_2(doc, "4.11 User Interface & Provenance Presentation")
    add_p(
        doc,
        "The user interface is implemented in app.py using Streamlit. It provides a clean, modern dashboard organized into three primary pages: "
        "(1) Claim Verification (input field, verdict banner, summary statistics, and reasoning trace), (2) Detailed Evidence (color-coded "
        "interactive cards for all Top-10 Fact-Checks and Top-10 PubMed articles with active hyperlinks to PMIDs), and (3) Evaluation Metrics "
        "(live rendering of Level 1 NLI metrics, Level 2 Decision Engine metrics, and confusion matrix tables)."
    )

    add_heading_2(doc, "4.12 Error Handling and System Resilience")
    add_p(
        doc,
        "To guarantee high system resilience, the codebase implements robust error handling:"
    )
    add_bullet_item(doc, "Native Pure-Python Metric Fallbacks: If scikit-learn is absent in the user's active Python environment, evaluation_metrics.py automatically executes built-in pure-Python/NumPy calculations for accuracy, precision, recall, F1, and confusion matrix, preventing crashes.", bold_prefix="Library Fallback: ")
    add_bullet_item(doc, "API Timeout & Rate-Limit Handling: Both Google Fact Check and PubMed retrieval connectors implement try-except blocks with graceful fallbacks to empty lists when external servers time out.", bold_prefix="Network Resilience: ")
    add_bullet_item(doc, "Offline HuggingFace Support: The evaluation pipeline checks for locally cached model weights (HF_HUB_OFFLINE=1) to allow evaluation without an active internet connection.", bold_prefix="Offline Execution: ")

    add_heading_2(doc, "4.13 Testing and Evaluation Subsystem Implementation")
    add_p(
        doc,
        "The evaluation subsystem consists of evaluation_metrics.py, evaluate_real_model.py, and evaluate_ranking.py. It loads labeled test "
        "datasets, passes claims through the real transformer models, and calculates classification accuracy, macro/weighted F1-scores, "
        "confusion matrices, and IR ranking metrics (MRR, P@K, R@K, NDCG@K)."
    )

    add_heading_2(doc, "4.14 Testing Procedures (Unit, Integration, Fallbacks)")
    add_p(
        doc,
        "The test suite is implemented in test_evaluation.py, containing eight automated unit and integration tests covering: "
        "(1) Symmetric 2-class baseline calculations, (2) Asymmetric 3-class class imbalance handling, (3) Empty dataset safety, "
        "(4) Missing and invalid label normalization, (5) Canonical alias mapping, (6) Saved prediction verification, (7) Expanded dataset "
        "integrity (N=60), and (8) Information retrieval ranking calculations (MRR, P@K, R@K). All 8 tests execute cleanly with a 100% pass rate."
    )

    add_heading_2(doc, "4.15 Implementation Limitations")
    add_bullet_item(doc, "English-Only Knowledge Corpus: The retrieval connectors currently query English-language PubMed citations and fact-checks.", bold_prefix="Language Limitation: ")
    add_bullet_item(doc, "CPU Latency: While bi-encoder ranking executes in milliseconds, running DeBERTa-v3-large across 20 candidate pairs on CPU requires approximately 10–14 seconds.", bold_prefix="Inference Latency: ")
    add_bullet_item(doc, "Abstract-Only PubMed Analysis: The system evaluates titles and abstracts; full-text XML papers are not analyzed due to paywalls and bandwidth constraints.", bold_prefix="Text Depth: ")

    add_heading_2(doc, "4.16 Chapter Summary")
    add_p(
        doc,
        "This chapter explained the concrete implementation of all eight modules comprising the verification system. It documented "
        "the Python libraries, retrieval limits, SBERT and MedCPT ranking algorithms, DeBERTa NLI stance classification, deterministic "
        "decision engine logic, Streamlit UI, error handling fallbacks, and the 8-stage automated test suite. The empirical results "
        "obtained from this implementation are evaluated in Chapter 5."
    )

print("Chapter 3 and Chapter 4 generator module created.")
