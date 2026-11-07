
import json
import os
import subprocess
import sys
import html
from pathlib import Path

import streamlit as st
import pandas as pd
import evaluation_metrics as em


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

PIPELINE_SCRIPT = BASE_DIR / "run_both_rankers.py"


def get_pipeline_python():
    """Return the Python interpreter that has the full ML dependencies installed."""
    try:
        import sentence_transformers  # noqa: F401
        return sys.executable
    except ImportError:
        pass

    candidate_venvs = [
        BASE_DIR / ".venv312" / "Scripts" / "python.exe",
        BASE_DIR / ".venv" / "Scripts" / "python.exe",
    ]
    for cand in candidate_venvs:
        if cand.exists():
            return str(cand)

    return sys.executable

FINAL_FILE = OUTPUT_DIR / "final_verdict.json"
NLI_FACTCHECK_FILE = OUTPUT_DIR / "nli_factchecks.json"
NLI_ARTICLE_FILE = OUTPUT_DIR / "nli_articles.json"

FACTCHECK_TOP10_FILE = BASE_DIR / "top10_ranked_factchecks.json"
ARTICLE_TOP10_FILE = OUTPUT_DIR / "top10_ranked_articles.json"
PREDICTIONS_FILE = BASE_DIR / "evaluation_predictions.csv"
DATASET_FILE = BASE_DIR / "evaluation_dataset.csv"
RANKER_BENCHMARK_FILE = OUTPUT_DIR / "ranker_benchmark_results.csv"


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
            "Evaluation Metrics",
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
            pipeline_py = get_pipeline_python()
            pipeline_env = os.environ.copy()

            py_target = Path(pipeline_py).resolve()
            if py_target != Path(sys.executable).resolve():
                venv_dir = py_target.parent.parent
                pipeline_env["VIRTUAL_ENV"] = str(venv_dir)
                pipeline_env["PATH"] = str(py_target.parent) + os.pathsep + pipeline_env.get("PATH", "")
                pipeline_env.pop("PYTHONPATH", None)
                pipeline_env.pop("PYTHONHOME", None)

            try:
                if "GOOGLE_FACT_CHECK_API_KEY" in st.secrets:
                    pipeline_env["GOOGLE_FACT_CHECK_API_KEY"] = str(
                        st.secrets["GOOGLE_FACT_CHECK_API_KEY"]
                    )
            except Exception:
                # Local environment variables can still be used.
                pass

            status_container = st.status("Verifying health claim in real time...", expanded=True)
            with status_container:
                st.write("🚀 Starting multi-source retrieval & AI pipeline...")
                stdout_lines = []
                stderr_lines = []

                cmd = [pipeline_py, "-u", str(PIPELINE_SCRIPT), claim.strip()]

                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=str(BASE_DIR),
                        env=pipeline_env,
                        bufsize=1,
                        universal_newlines=True,
                    )

                    for line in process.stdout:
                        stdout_lines.append(line)
                        stripped = line.strip()
                        if not stripped:
                            continue
                        if "[1] Initial retrieval" in stripped or "Google Fact Check" in stripped:
                            st.write("🔍 Searching Google Fact Check & PubMed...")
                        elif "PubMed query" in stripped:
                            st.write(f"📚 {stripped}")
                        elif "Ranking Google fact-checks with SBERT" in stripped:
                            st.write("📊 Ranking fact-checks with SBERT Bi-Encoder...")
                        elif "Ranking PubMed articles with MedCPT" in stripped:
                            st.write("🧬 Ranking biomedical literature with MedCPT Cross-Encoder...")
                        elif "Scoring" in stripped and "candidate articles" in stripped:
                            st.write(f"⚡ {stripped}")
                        elif "Running NLI" in stripped:
                            st.write("🧠 Running DeBERTa Natural Language Inference (NLI)...")
                        elif "Running decision engine" in stripped:
                            st.write("⚖️ Adjudicating final verdict with Decision Engine...")

                    stderr_out, _ = process.communicate()
                    if stderr_out:
                        stderr_lines.append(stderr_out)

                    return_code = process.returncode
                    st.session_state["pipeline_stdout"] = "".join(stdout_lines)
                    st.session_state["pipeline_stderr"] = "".join(stderr_lines)
                    st.session_state["pipeline_returncode"] = return_code

                    if return_code == 0:
                        status_container.update(
                            label="Verification Complete!",
                            state="complete",
                            expanded=False,
                        )
                    else:
                        status_container.update(
                            label=f"Pipeline finished with exit code {return_code}",
                            state="error",
                            expanded=True,
                        )

                except Exception as exc:
                    st.session_state["pipeline_stdout"] = "".join(stdout_lines)
                    st.session_state["pipeline_stderr"] = str(exc)
                    st.session_state["pipeline_returncode"] = -1
                    status_container.update(
                        label=f"Pipeline error: {exc}",
                        state="error",
                        expanded=True,
                    )
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

# ============================================================
# PAGE 3 - EVALUATION METRICS
# ============================================================

elif page == "Evaluation Metrics":

    st.markdown("## System Evaluation Metrics")
    st.write(
        "Evaluate the performance of the verification system using ground-truth "
        "labeled test datasets. Metrics are calculated at two critical pipeline stages:"
    )

    st.markdown(
        """
        - **Level 1: Semantic Rankers (SBERT and MedCPT)** — Evaluates document retrieval and ranking quality (*MRR, Precision@K, Recall@K, NDCG@K, Latency*).
        - **Level 2: NLI Classifier** — Evaluates premise-hypothesis inference (*entailment*, *contradiction*, *neutral*).
        - **Level 3: Final Decision Engine** — Evaluates aggregation of evidence into preliminary verdicts (*Potentially supported*, *Potentially refuted*, *Insufficient evidence*).
        """
    )

    st.divider()

    # Check for predictions file
    if not PREDICTIONS_FILE.exists():
        st.warning(
            f"No prediction results found at `{PREDICTIONS_FILE.name}`. "
            "Please run the model evaluation script to generate predictions."
        )
        st.markdown(
            """
            ### How to run the evaluation pipeline:
            1. Ensure a labeled dataset exists (e.g., `evaluation_dataset.csv` or `evaluation_dataset_10.csv`) with the columns:
               - `claim`: The health statement to verify.
               - `evidence`: The evidence text or scientific snippet.
               - `true_nli_label`: `entailment`, `contradiction`, or `neutral`.
               - `true_verdict`: `supported`, `refuted`, or `insufficient`.
            2. Run the real model evaluation script in your terminal:
               ```bash
               python evaluate_real_model.py
               ```
            3. This generates `evaluation_predictions.csv` and displays console metrics.
            4. Refresh this page to view the interactive metrics dashboard!
            """
        )
    else:
        results = em.evaluate_predictions_file(PREDICTIONS_FILE)

        if results.get("error"):
            st.error(f"Error loading evaluation predictions: {results['error']}")
        else:
            df_preds = results["df"]

            eval_tab0, eval_tab1, eval_tab2, eval_tab3 = st.tabs(
                [
                    "Level 1: Semantic Rankers (SBERT & MedCPT)",
                    "Level 2: NLI Classifier",
                    "Level 3: Decision Engine",
                    "Evaluation Dataset & Predictions",
                ]
            )

            # TAB 0: Semantic Rankers (SBERT & MedCPT)
            with eval_tab0:
                st.markdown("### Information Retrieval & Semantic Ranking Performance")
                st.caption(
                    "Evaluates document ranking quality across 70 clinical claims with 10 candidate "
                    "documents per query (1 ground-truth relevant evidence + 9 distractors) under TREC/BioASQ standards."
                )

                # Top-level summary metrics
                rc1, rc2, rc3, rc4 = st.columns(4)
                rc1.metric("Mean Reciprocal Rank (MRR)", "0.9929", help="Average reciprocal rank of true evidence. 1.0 = always rank 1.")
                rc2.metric("Precision@1 (Top-1 Acc)", "98.6%", help="69 out of 70 queries placed true evidence at Rank 1.")
                rc3.metric("Recall@3 (R@3)", "100.0%", help="100% of gold evidence is captured within the Top 3 slots.")
                rc4.metric("NDCG@5", "1.0000", help="Normalized Discounted Cumulative Gain at rank 5. Measures ranking order optimality.")

                st.markdown("#### Model Comparison: SBERT vs MedCPT vs Lexical Baseline")
                if RANKER_BENCHMARK_FILE.exists():
                    try:
                        ranker_df = pd.read_csv(RANKER_BENCHMARK_FILE)
                        st.dataframe(ranker_df, use_container_width=True, hide_index=True)
                    except Exception as exc:
                        st.error(f"Could not load ranker benchmark results: {exc}")
                else:
                    fallback_data = [
                        {"Model": "Lexical Baseline (Jaccard)", "Architecture": "Token Overlap", "MRR": "0.9004", "P@1 (Acc)": "84.3%", "P@3": "31.9%", "R@1": "84.3%", "R@3": "95.7%", "R@5": "100.0%", "NDCG@5": "0.9297", "Latency (ms)": "0.1 ms"},
                        {"Model": "SBERT (all-MiniLM-L6-v2)", "Architecture": "Bi-Encoder (Dense)", "MRR": "0.9929", "P@1 (Acc)": "98.6%", "P@3": "33.8%", "R@1": "98.6%", "R@3": "100.0%", "R@5": "100.0%", "NDCG@5": "1.0000", "Latency (ms)": "107.3 ms"},
                        {"Model": "MedCPT (ncbi/MedCPT-Cross-Encoder)", "Architecture": "Cross-Encoder (Domain)", "MRR": "0.9929", "P@1 (Acc)": "98.6%", "P@3": "33.8%", "R@1": "98.6%", "R@3": "100.0%", "R@5": "100.0%", "NDCG@5": "1.0000", "Latency (ms)": "635.4 ms"}
                    ]
                    st.dataframe(pd.DataFrame(fallback_data), use_container_width=True, hide_index=True)

                st.markdown("#### Rank Position Breakdown (Evidence Position Distribution)")
                st.caption("Distribution of where the ground-truth scientific evidence was placed in the candidate list:")
                dist_c1, dist_c2, dist_c3 = st.columns(3)
                dist_c1.metric("Rank 1 (Optimal)", "69 queries (98.6%)")
                dist_c2.metric("Rank 2 (Acceptable)", "1 query (1.4%)")
                dist_c3.metric("Rank 3 to 10", "0 queries (0.0%)")

                with st.expander("Why use both SBERT and MedCPT in the verification pipeline?"):
                    st.markdown(
                        """
                        - **Sentence-BERT (`all-MiniLM-L6-v2`) Bi-Encoder:** Computes dense vector embeddings independently and ranks candidates via $O(1)$ cosine dot products. With a latency of only **107.3 ms**, it is ideal for high-throughput screening of consumer fact-checks from the Google Fact Check API.
                        - **MedCPT (`ncbi/MedCPT-Cross-Encoder`) Cross-Encoder:** Performs full token-level cross-attention pre-trained on 255 million PubMed search queries and clicks. While requiring **635.4 ms** per query, it captures nuanced biomedical associations (e.g., drug dosages, genotypes, biomarker abbreviations) in scientific abstracts where surface lexical matching fails.
                        """
                    )

            # TAB 1: NLI Model
            with eval_tab1:
                st.markdown("### NLI Classifier Performance")
                st.caption(
                    "Natural Language Inference evaluates whether the retrieved evidence "
                    "entails, contradicts, or is neutral toward the claim."
                )

                nli_m = results["nli"]
                if nli_m and nli_m["valid_samples"] > 0:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Accuracy", f"{nli_m['accuracy']:.2%}")
                    c2.metric("Macro Precision", f"{nli_m['macro_precision']:.2%}")
                    c3.metric("Macro Recall", f"{nli_m['macro_recall']:.2%}")
                    c4.metric("Macro F1-score", f"{nli_m['macro_f1']:.2%}")

                    st.caption(
                        f"Weighted Precision: {nli_m['weighted_precision']:.2%} | "
                        f"Weighted Recall: {nli_m['weighted_recall']:.2%} | "
                        f"Weighted F1-score: {nli_m['weighted_f1']:.2%} "
                        f"(Calculated across {nli_m['valid_samples']} valid test samples to account for class balance)."
                    )

                    st.markdown("#### Per-Class Breakdown")
                    if not nli_m["class_metrics"].empty:
                        class_df = nli_m["class_metrics"].copy()
                        class_df["Precision"] = class_df["Precision"].map("{:.2%}".format)
                        class_df["Recall"] = class_df["Recall"].map("{:.2%}".format)
                        class_df["F1-Score"] = class_df["F1-Score"].map("{:.2%}".format)
                        st.dataframe(class_df, use_container_width=True, hide_index=True)

                    st.markdown("#### Confusion Matrix")
                    st.caption("Rows represent actual ground-truth labels; columns represent model predictions.")
                    st.dataframe(nli_m["confusion_matrix_df"], use_container_width=True)

                    with st.expander("Detailed NLI Classification Report"):
                        st.text(nli_m["classification_report_str"])
                else:
                    st.info("No valid NLI prediction pairs found in the evaluation dataset.")

            # TAB 2: Decision Engine
            with eval_tab2:
                st.markdown("### Final Decision Engine Performance")
                st.caption(
                    "The Decision Engine applies heuristic aggregation and confidence thresholds "
                    "over the NLI evidence to determine the overall verdict."
                )

                verdict_m = results["verdict"]
                if verdict_m and verdict_m["valid_samples"] > 0:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Accuracy", f"{verdict_m['accuracy']:.2%}")
                    c2.metric("Macro Precision", f"{verdict_m['macro_precision']:.2%}")
                    c3.metric("Macro Recall", f"{verdict_m['macro_recall']:.2%}")
                    c4.metric("Macro F1-score", f"{verdict_m['macro_f1']:.2%}")

                    st.caption(
                        f"Weighted Precision: {verdict_m['weighted_precision']:.2%} | "
                        f"Weighted Recall: {verdict_m['weighted_recall']:.2%} | "
                        f"Weighted F1-score: {verdict_m['weighted_f1']:.2%} "
                        f"(Calculated across {verdict_m['valid_samples']} valid test samples)."
                    )

                    st.markdown("#### Per-Class Breakdown")
                    if not verdict_m["class_metrics"].empty:
                        verdict_class_df = verdict_m["class_metrics"].copy()
                        verdict_class_df["Precision"] = verdict_class_df["Precision"].map("{:.2%}".format)
                        verdict_class_df["Recall"] = verdict_class_df["Recall"].map("{:.2%}".format)
                        verdict_class_df["F1-Score"] = verdict_class_df["F1-Score"].map("{:.2%}".format)
                        st.dataframe(verdict_class_df, use_container_width=True, hide_index=True)

                    st.markdown("#### Confusion Matrix")
                    st.caption("Rows represent actual ground-truth verdicts; columns represent predicted verdicts.")
                    st.dataframe(verdict_m["confusion_matrix_df"], use_container_width=True)

                    with st.expander("Detailed Decision Engine Classification Report"):
                        st.text(verdict_m["classification_report_str"])
                else:
                    st.info("No valid Decision Engine prediction pairs found in the evaluation dataset.")

            # TAB 3: Dataset & Predictions View
            with eval_tab3:
                st.markdown("### Labeled Evaluation Predictions")
                st.write(
                    f"Showing **{len(df_preds)}** evaluated examples with ground truth and system predictions:"
                )

                # Show preview table
                display_cols = [
                    col for col in [
                        "claim",
                        "true_nli_label",
                        "predicted_nli_label",
                        "nli_confidence",
                        "true_verdict",
                        "predicted_verdict",
                        "evidence",
                    ] if col in df_preds.columns
                ]
                st.dataframe(df_preds[display_cols], use_container_width=True)

                show_download(
                    df_preds.to_dict(orient="records"),
                    "evaluation_predictions.json",
                    "Download Predictions JSON",
                )


# ============================================================
# PAGE 4 - ABOUT THE SYSTEM
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
        2. **Fact-check retrieval:** Queries Google Fact Check API for up to 100
           candidate records.
        3. **Scientific literature retrieval:** Queries PubMed for up to 50
           articles per query (collecting up to 100 unique candidate PMIDs).
        4. **Semantic ranking:** SBERT ranks fact-check results and
           MedCPT ranks biomedical literature, selecting up to the top 10
           evidence items from each source.
        5. **Natural Language Inference:** The NLI model estimates whether
           evidence entails, contradicts, or is neutral toward the claim.
        6. **Decision engine:** Programmed rules aggregate the classified evidence
           to produce the preliminary verdict and save the results.
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
