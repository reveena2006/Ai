
import json
import os
import subprocess
import sys
import html
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

PIPELINE_SCRIPT = BASE_DIR / "run_both_rankers.py"

FINAL_FILE = OUTPUT_DIR / "final_verdict.json"
NLI_FACTCHECK_FILE = OUTPUT_DIR / "nli_factchecks.json"
NLI_ARTICLE_FILE = OUTPUT_DIR / "nli_articles.json"

FACTCHECK_TOP10_FILE = BASE_DIR / "top10_ranked_factchecks.json"
ARTICLE_TOP10_FILE = OUTPUT_DIR / "top10_ranked_articles.json"


# ============================================================
# STREAMLIT PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI Assisted Health Information Verification System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)



# ============================================================
# CUSTOM CSS - LARGE FONTS AND WHITE INPUT TEXT
# ============================================================

st.markdown(
    """
    <style>
    /* Main application */
    .stApp {
        background-color: #f3f6fb;
        color: #1e293b;
        font-size: 19px;
    }

    /* Main content text */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .main p,
    .main li,
    .main label,
    .main [data-testid="stMarkdownContainer"] {
        font-size: 19px;
        line-height: 1.65;
        color: #1e293b;
    }

    /* Main title */
    .main-title {
        font-size: 38px !important;
        font-weight: 800;
        line-height: 1.35;
        color: #10243a !important;
        margin-bottom: 12px;
    }

    .subtitle {
        font-size: 19px !important;
        color: #475569 !important;
        margin-bottom: 28px;
    }

    .section-title,
    .main h1 {
        font-size: 31px !important;
        font-weight: 750;
        color: #10243a !important;
    }

    .main h2 {
        font-size: 27px !important;
        color: #10243a !important;
    }

    .main h3 {
        font-size: 23px !important;
        color: #10243a !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #10243a;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
        font-size: 17px;
    }

    /* Claim text area: WHITE TEXT on DARK BACKGROUND */
    .stTextArea textarea {
        background-color: #202733 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        border: 2px solid #64748b !important;
        border-radius: 10px !important;
    }

    .stTextArea textarea::placeholder {
        color: #d1d5db !important;
        -webkit-text-fill-color: #d1d5db !important;
        opacity: 1 !important;
    }

    .stTextArea textarea:focus {
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    /* Input labels */
    .stTextArea label,
    .stTextInput label {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #10243a !important;
    }

    /* Result cards */
    .result-card {
        background-color: #ffffff;
        border: 1px solid #dbe4ef;
        border-radius: 14px;
        padding: 25px;
        margin: 15px 0;
    }

    .small-label {
        color: #475569 !important;
        font-size: 17px !important;
        margin-bottom: 8px;
    }

    .claim-text {
        color: #10243a !important;
        font-size: 23px !important;
        font-weight: 700;
        overflow-wrap: anywhere;
    }

    .verdict-text {
        color: #14532d !important;
        font-size: 31px !important;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    /* Evidence text and expandable panels */
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #dbe4ef;
        border-radius: 10px;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p {
        color: #10243a !important;
        font-size: 19px !important;
        font-weight: 600;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #334155 !important;
        font-size: 18px !important;
        font-weight: 650 !important;
    }

    .stTabs [aria-selected="true"] {
        color: #1769aa !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dbe4ef;
        border-radius: 12px;
        padding: 18px;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #475569 !important;
        font-size: 17px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #10243a !important;
        font-size: 32px !important;
    }

    /* Buttons */
    div.stButton > button,
    div[data-testid="stDownloadButton"] button {
        background-color: #1769aa !important;
        color: #ffffff !important;
        font-size: 19px !important;
        font-weight: 700 !important;
        border: none;
        border-radius: 10px;
        min-height: 48px;
        padding: 10px 20px;
    }

    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #12548a !important;
        color: #ffffff !important;
    }

    /* Notices and disclaimers */
    .disclaimer {
        background-color: #fff7e6;
        border-left: 5px solid #e6a23c;
        border-radius: 8px;
        padding: 18px;
        color: #614b20 !important;
        font-size: 18px !important;
        line-height: 1.7;
    }

    /* Metric and general captions */
    [data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-size: 16px !important;
    }

    /* Code and JSON viewers */
    .stCode,
    .stCode pre,
    div[data-testid="stJson"] {
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# JSON AND DATA HELPERS
# ============================================================

def load_json(path):
    """Load a JSON file and report errors without crashing the UI."""
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        st.error(f"Could not read {path.name}: {exc}")
        return None


def get_text(data, keys, default="Not available"):
    """Return the first non-empty value matching one of the keys."""
    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if value is not None and value != "":
            return value

    return default


def as_text(value, default="Not available"):
    if value is None or value == "":
        return default

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)


def get_records(data):
    """Accept lists directly or lists stored inside common JSON keys."""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "results",
            "records",
            "articles",
            "factchecks",
            "evidence",
            "ranked_results",
            "accepted_evidence",
            "rejected_evidence",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def get_claim(data):
    return as_text(
        get_text(data, ["user_claim", "claim", "input_claim"], ""),
        default="",
    )


def get_verdict(data):
    return as_text(
        get_text(
            data,
            [
                "verdict",
                "final_verdict",
                "decision",
                "classification",
                "status",
            ],
            "Insufficient evidence",
        )
    )


def get_evidence_lists(data):
    """Support both newer and older decision-engine output formats."""
    if not isinstance(data, dict):
        return [], []

    accepted = get_text(
        data,
        [
            "accepted_evidence",
            "supporting_evidence",
            "relevant_evidence",
        ],
        [],
    )

    rejected = get_text(
        data,
        [
            "rejected_evidence",
            "excluded_evidence",
            "irrelevant_evidence",
        ],
        [],
    )

    if not isinstance(accepted, list):
        accepted = []

    if not isinstance(rejected, list):
        rejected = []

    # Some outputs store evidence inside a nested result object.
    if not accepted and isinstance(data.get("results"), dict):
        nested = data["results"]
        accepted = nested.get("accepted_evidence", [])
        rejected = nested.get("rejected_evidence", [])

        if not isinstance(accepted, list):
            accepted = []

        if not isinstance(rejected, list):
            rejected = []

    return accepted, rejected


def get_nli_label(record):
    return str(
        get_text(
            record,
            ["nli_label", "label", "prediction", "classification"],
            "Unclassified",
        )
    ).lower()


def count_labels(records):
    support = 0
    contradiction = 0
    neutral = 0
    other = 0

    for record in records:
        if not isinstance(record, dict):
            other += 1
            continue

        label = get_nli_label(record)

        if "contradict" in label or "refut" in label:
            contradiction += 1
        elif "entail" in label or "support" in label:
            support += 1
        elif "neutral" in label:
            neutral += 1
        else:
            other += 1

    return support, contradiction, neutral, other


def show_download(data, filename, label):
    if data is None:
        return

    content = json.dumps(data, indent=2, ensure_ascii=False)

    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime="application/json",
        key=f"download_{filename}",
    )


# ============================================================
# EVIDENCE DISPLAY
# ============================================================

def show_evidence(records, empty_message="No evidence records are available."):
    if not records:
        st.info(empty_message)
        return

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            record = {"evidence": str(record)}

        title = get_text(
            record,
            [
                "title",
                "evidence_title",
                "article_title",
                "claim",
            ],
            f"Evidence {index}",
        )

        source = get_text(
            record,
            [
                "source",
                "publisher",
                "source_name",
                "journal",
                "website",
                "domain",
            ],
            "Source not specified",
        )

        label = get_text(
            record,
            ["nli_label", "label", "prediction"],
            "Not classified",
        )

        # Prefer the NLI evidence text, then fall back to source text.
        evidence_text = get_text(
            record,
            [
                "nli_evidence_text",
                "abstract",
                "snippet",
                "text",
                "evidence",
                "description",
                "claim_text",
                "content",
            ],
            "No evidence text was stored in this record.",
        )

        with st.expander(f"{index}. {as_text(title)}"):
            st.markdown(f"**Source:** {as_text(source)}")
            st.markdown(f"**NLI classification:** {as_text(label)}")

            confidence = get_text(
                record,
                ["nli_confidence", "confidence"],
                None,
            )

            if confidence is not None:
                st.markdown(
                    f"**Model confidence:** {as_text(confidence)}"
                )

            st.markdown("**Evidence text**")
            st.write(as_text(evidence_text))

            url = get_text(
                record,
                ["url", "link", "source_url", "article_url"],
                None,
            )

            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.markdown(f"[Open original source]({url})")

            with st.expander("Inspect complete evidence record"):
                st.json(record)


# ============================================================
# RESULTS PAGE
# ============================================================

def render_results(final_data):
    if not isinstance(final_data, dict):
        st.warning(
            "No valid final verdict is available. Run a claim verification first."
        )
        return

    claim = get_claim(final_data)
    verdict = get_verdict(final_data)
    accepted, rejected = get_evidence_lists(final_data)

    factcheck_data = load_json(NLI_FACTCHECK_FILE)
    article_data = load_json(NLI_ARTICLE_FILE)

    factcheck_records = get_records(factcheck_data)
    article_records = get_records(article_data)

    all_nli_records = factcheck_records + article_records

    support, contradiction, neutral, other = count_labels(all_nli_records)

    st.markdown("## Verification Result")

    # Escape user-provided text before rendering it as HTML.
    safe_claim = html.escape(claim or "Claim not included in output.")
    safe_verdict = html.escape(verdict)

    st.markdown(
        f"""
        <div class="result-card">
            <div class="small-label">Submitted health claim</div>
            <div class="claim-text">{safe_claim}</div>
            <hr>
            <div class="small-label">System assessment</div>
            <div class="verdict-text">{safe_verdict}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Evidence Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Accepted evidence", len(accepted))
    c2.metric("Rejected evidence", len(rejected))
    c3.metric("Support-labelled items", support)
    c4.metric("Contradiction-labelled items", contradiction)

    st.caption(
        f"Neutral-labelled items: {neutral} | "
        f"Other or unrecognized NLI labels: {other}. "
        "These counts describe model outputs, not verified medical facts."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Accepted Evidence",
            "Rejected Evidence",
            "Source Analysis",
            "Limitations",
        ]
    )

    with tab1:
        st.markdown("### Evidence retained by the decision engine")
        show_evidence(
            accepted,
            "The decision engine did not return accepted evidence.",
        )

    with tab2:
        st.markdown("### Evidence not retained by the decision engine")
        show_evidence(
            rejected,
            "The decision engine did not return rejected evidence.",
        )

    with tab3:
        st.markdown("### Google Fact Check evidence")

        if factcheck_data is None:
            st.info("The NLI fact-check output file was not found.")
        else:
            st.write(f"Records available: {len(factcheck_records)}")
            show_evidence(factcheck_records)

        st.divider()

        st.markdown("### PubMed scientific literature")

        if article_data is None:
            st.info("The NLI PubMed output file was not found.")
        else:
            st.write(f"Records available: {len(article_records)}")
            show_evidence(article_records)

    with tab4:
        st.markdown("### How to interpret this result")

        st.markdown(
            """
            - Google Fact Check and PubMed provide retrieved source material.
            - SBERT and MedCPT rank information for relevance.
            - The NLI model estimates whether evidence entails, contradicts,
              or is neutral toward the claim.
            - The decision engine applies programmed rules to produce
              a preliminary assessment.
            - The assessment can be wrong or incomplete and is not a
              medical diagnosis.
            - Review the original sources and consult a qualified
              healthcare professional for medical decisions.
            """
        )

    st.divider()

    show_download(
        final_data,
        "final_verdict.json",
        "Download Final Verdict JSON",
    )

    show_download(
        factcheck_data,
        "nli_factchecks.json",
        "Download Fact-check NLI JSON",
    )

    show_download(
        article_data,
        "nli_articles.json",
        "Download PubMed NLI JSON",
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown("## 🩺 HealthVerify")
    st.caption("AI-assisted health information analysis")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Check a Claim",
            "Latest Results",
            "About the System",
        ],
    )

    st.divider()

    st.caption(
        "Research support tool. Results should not be treated as "
        "a medical diagnosis."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        AI Assisted Health Information Verification System
    </div>
    <div class="subtitle">
        Analyze health claims using fact-check retrieval, scientific literature,
        semantic ranking, and natural language inference.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE 1 - CHECK A CLAIM
# ============================================================

if page == "Check a Claim":

    st.markdown(
        '<div class="section-title">Verify a Health Claim</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Enter a health-related statement to retrieve relevant evidence "
        "and generate a preliminary assessment."
    )

    claim = st.text_area(
        "Health claim",
        value=st.session_state.get(
            "current_claim",
            "Osteoarthritis only affects older people",
        ),
        height=120,
        placeholder="Enter a health claim to check...",
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        run_clicked = st.button(
            "Verify Claim",
            type="primary",
            use_container_width=True,
        )

    with col2:
        st.caption(
            "Retrieval and model inference may take several minutes."
        )

    if run_clicked:
        if not claim.strip():
            st.error("Please enter a health claim.")

        elif not PIPELINE_SCRIPT.exists():
            st.error(
                f"Pipeline script not found: {PIPELINE_SCRIPT}"
            )

        else:
            st.session_state["current_claim"] = claim.strip()

            # Make sure the output directory exists.
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            # Remove the previous final verdict so a failed new run
            # cannot silently display an old verdict as a fresh result.
            if FINAL_FILE.exists():
                try:
                    FINAL_FILE.unlink()
                except OSError as exc:
                    st.error(
                        "Could not clear the previous verdict file. "
                        f"Please close any program using it. Details: {exc}"
                    )
                    st.stop()

            # Pass the API key to the child process when configured.
            pipeline_env = os.environ.copy()

            try:
                if "GOOGLE_FACT_CHECK_API_KEY" in st.secrets:
                    pipeline_env["GOOGLE_FACT_CHECK_API_KEY"] = str(
                        st.secrets["GOOGLE_FACT_CHECK_API_KEY"]
                    )
            except Exception:
                # Local environment variables can still be used.
                pass

            st.info(
                "Verification is running. Please keep this page open "
                "until the process finishes."
            )

            with st.spinner(
                "Retrieving sources, ranking evidence, and running NLI..."
            ):
                try:
                    process = subprocess.run(
                        [sys.executable, str(PIPELINE_SCRIPT)],
                        input=claim.strip() + "\n",
                        text=True,
                        capture_output=True,
                        cwd=str(BASE_DIR),
                        timeout=1800,
                        check=False,
                        env=pipeline_env,
                    )

                    st.session_state["pipeline_stdout"] = process.stdout
                    st.session_state["pipeline_stderr"] = process.stderr
                    st.session_state["pipeline_returncode"] = process.returncode

                except subprocess.TimeoutExpired as exc:
                    st.session_state["pipeline_stdout"] = (
                        exc.stdout.decode(errors="replace")
                        if isinstance(exc.stdout, bytes)
                        else (exc.stdout or "")
                    )
                    st.session_state["pipeline_stderr"] = (
                        exc.stderr.decode(errors="replace")
                        if isinstance(exc.stderr, bytes)
                        else (exc.stderr or "")
                    )
                    st.session_state["pipeline_returncode"] = -1

                    st.error(
                        "The pipeline exceeded the 30-minute time limit. "
                        "Check the logs and model/retrieval runtime."
                    )

                except Exception as exc:
                    st.session_state["pipeline_stdout"] = ""
                    st.session_state["pipeline_stderr"] = str(exc)
                    st.session_state["pipeline_returncode"] = -1

                    st.error(f"Could not run the pipeline: {exc}")

            # Display pipeline logs for troubleshooting.
            with st.expander("Pipeline Logs", expanded=False):
                st.markdown("**Standard output**")
                st.code(
                    st.session_state.get("pipeline_stdout")
                    or "No standard output captured."
                )

                st.markdown("**Errors and warnings**")
                st.code(
                    st.session_state.get("pipeline_stderr")
                    or "No error output captured."
                )

            return_code = st.session_state.get(
                "pipeline_returncode", -1
            )

            if return_code == 0:
                st.success("Pipeline process finished.")
            elif return_code != -1:
                st.error(
                    f"The pipeline exited with return code {return_code}."
                )

            # Only show a result if the new pipeline produced the file.
            if FINAL_FILE.exists():
                final_data = load_json(FINAL_FILE)

                if isinstance(final_data, dict):
                    output_claim = get_claim(final_data)

                    if (
                        output_claim
                        and output_claim.strip().casefold()
                        != claim.strip().casefold()
                    ):
                        st.error(
                            "The saved verdict belongs to a different claim. "
                            "Check the claim handling in your pipeline."
                        )
                    else:
                        render_results(final_data)

                else:
                    st.error(
                        "The pipeline output exists, but it is not valid JSON."
                    )

            else:
                st.error(
                    "No new final_verdict.json was produced. "
                    "Open Pipeline Logs above and check decision_engine.py."
                )

    # Show an existing saved result when no new claim is submitted.
    else:
        if FINAL_FILE.exists():
            saved_data = load_json(FINAL_FILE)

            if isinstance(saved_data, dict):
                st.markdown("---")
                st.markdown("### Most Recent Saved Result")
                render_results(saved_data)
        else:
            st.info(
                "Enter a claim and click Verify Claim to begin."
            )


# ============================================================
# PAGE 2 - LATEST RESULTS
# ============================================================

elif page == "Latest Results":

    st.markdown("## Latest Verification Results")

    final_data = load_json(FINAL_FILE)

    if final_data is None:
        st.info(
            "No saved verdict is available yet. Go to Check a Claim "
            "and run the verification pipeline."
        )
    else:
        render_results(final_data)

    with st.expander("View ranked source files"):

        ranking_files = {
            "Top 10 Google Fact Checks": FACTCHECK_TOP10_FILE,
            "Top 10 PubMed Articles": ARTICLE_TOP10_FILE,
        }

        for label, path in ranking_files.items():
            st.markdown(f"### {label}")

            data = load_json(path)

            if data is None:
                st.info(f"{path.name} has not been generated.")
            else:
                st.json(data)

                show_download(
                    data,
                    path.name,
                    f"Download {path.name}",
                )


# ============================================================
# PAGE 3 - ABOUT THE SYSTEM
# ============================================================

elif page == "About the System":

    st.markdown("## About the System")

    st.write(
        """
        The AI Assisted Health Information Verification System is a research
        prototype intended to help users examine health-related claims using
        retrieved information and natural language processing models.
        """
    )

    st.markdown("### System workflow")

    st.markdown(
        """
        1. **Claim input:** The user enters a health-related statement.
        2. **Fact-check retrieval:** Available Google Fact Check material
           is retrieved through the configured API.
        3. **Scientific literature retrieval:** PubMed is searched for
           potentially relevant biomedical articles.
        4. **Semantic ranking:** SBERT ranks fact-check results and
           MedCPT ranks biomedical literature.
        5. **Natural Language Inference:** The NLI model estimates the
           relationship between evidence passages and the claim.
        6. **Decision engine:** Programmed rules produce a preliminary
           assessment and save the results.
        """
    )

    st.markdown("### Technologies")

    st.markdown(
        """
        - Python
        - Streamlit
        - Google Fact Check API
        - PubMed
        - Sentence-BERT (SBERT)
        - MedCPT
        - Natural Language Inference (NLI)
        """
    )

    st.markdown(
        """
        <div class="disclaimer">
            <strong>Important:</strong> This is a research prototype.
            Model predictions may be incomplete or incorrect. The output
            does not establish medical truth and must not be used as the
            sole basis for healthcare decisions. Consult reliable sources
            and qualified healthcare professionals.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Assisted Health Information Verification System | "
    "Research prototype | Results depend on source availability "
    "and model predictions."
)
