"""
Generates the Preliminary Pages, Chapter 1 (Introduction), and Chapter 2 (Literature Review)
for the AI-Assisted Health-Related Misinformation Verification System project report.
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_helpers import (
    add_p, add_heading_1, add_heading_2, add_heading_3,
    add_bullet_item, add_numbered_item, format_table, add_callout,
    set_cell_margins
)

def build_preliminary_pages(doc):
    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(36)
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("[COLLEGE NAME / INSTITUTION LOGO PLACEHOLDER]\n[AFFILIATED UNIVERSITY / AUTONOMOUS INSTITUTION]")
    r_inst.bold = True
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(14)
    r_inst.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(4)
    p_dept.paragraph_format.space_after = Pt(36)
    r_dept = p_dept.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING")
    r_dept.bold = True
    r_dept.font.name = "Times New Roman"
    r_dept.font.size = Pt(13)
    r_dept.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(24)
    p_title.paragraph_format.line_spacing = 1.2
    r_title = p_title.add_run("AI-ASSISTED HEALTH-RELATED MISINFORMATION VERIFICATION SYSTEM")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(19)
    r_title.font.color.rgb = RGBColor(0, 0, 0)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(18)
    p_sub.paragraph_format.space_after = Pt(36)
    r_sub = p_sub.add_run(
        "A PROJECT REPORT\n"
        "Submitted in partial fulfillment of the requirements for the award of the degree of\n"
        "BACHELOR OF TECHNOLOGY / BACHELOR OF ENGINEERING\n"
        "IN\n"
        "COMPUTER SCIENCE AND ENGINEERING"
    )
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(36)
    p_meta.paragraph_format.space_after = Pt(24)
    r_meta = p_meta.add_run(
        "Submitted by:\n"
        "[STUDENT NAME]\n"
        "Register Number: [STUDENT REGISTER NUMBER]\n\n"
        "Under the Guidance and Supervision of:\n"
        "[PROJECT GUIDE NAME], [DESIGNATION / PH.D.]\n"
        "Department of Computer Science and Engineering\n\n"
        "ACADEMIC YEAR: [2025 – 2026]"
    )
    r_meta.font.name = "Times New Roman"
    r_meta.font.size = Pt(11.5)
    r_meta.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)

    # -------------------------------------------------------------
    # 2. BONAFIDE CERTIFICATE
    # -------------------------------------------------------------
    doc.add_page_break()
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(24)
    p_cert_title.paragraph_format.space_after = Pt(24)
    r_cert_title = p_cert_title.add_run("BONAFIDE CERTIFICATE")
    r_cert_title.bold = True
    r_cert_title.font.name = "Times New Roman"
    r_cert_title.font.size = Pt(15)

    add_p(
        doc,
        "This is to certify that the project report entitled 'AI-ASSISTED HEALTH-RELATED MISINFORMATION VERIFICATION SYSTEM' "
        "is the bonafide work of [STUDENT NAME] (Register Number: [STUDENT REGISTER NUMBER]), who carried out the project work "
        "under my supervision in partial fulfillment of the requirements for the award of the degree of Bachelor of Engineering / "
        "Bachelor of Technology in Computer Science and Engineering at [COLLEGE NAME], affiliated with [UNIVERSITY NAME], during the "
        "academic year [2025–2026]."
    )

    add_p(
        doc,
        "To the best of our knowledge and belief, this project report embodies original work completed by the candidate and has not "
        "formed the basis for the award of any other Degree, Diploma, Associateship, Fellowship, or similar title in this or any other "
        "educational institution."
    )

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(60)
    p_sig.paragraph_format.space_after = Pt(12)
    p_sig.paragraph_format.line_spacing = 1.3
    r_sig = p_sig.add_run(
        "_____________________________                           _____________________________\n"
        "SIGNATURE OF GUIDE                                     SIGNATURE OF HEAD OF DEPARTMENT\n"
        "[PROJECT GUIDE NAME], [DEGREE]                         [HOD NAME], [DEGREE]\n"
        "Project Supervisor / Assistant Professor               Head of the Department\n"
        "Department of Computer Science & Engineering           Department of Computer Science & Engineering\n"
        "[COLLEGE NAME]                                         [COLLEGE NAME]"
    )
    r_sig.font.name = "Times New Roman"
    r_sig.font.size = Pt(11)

    p_viva = doc.add_paragraph()
    p_viva.paragraph_format.space_before = Pt(36)
    p_viva.paragraph_format.line_spacing = 1.3
    r_viva = p_viva.add_run(
        "Submitted for the University Project Viva-Voce Examination held on: [DATE OF EXAMINATION]\n\n\n"
        "_____________________________                           _____________________________\n"
        "INTERNAL EXAMINER                                      EXTERNAL EXAMINER"
    )
    r_viva.font.name = "Times New Roman"
    r_viva.font.size = Pt(11)

    # -------------------------------------------------------------
    # 3. STUDENT DECLARATION
    # -------------------------------------------------------------
    doc.add_page_break()
    p_dec_title = doc.add_paragraph()
    p_dec_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dec_title.paragraph_format.space_before = Pt(24)
    p_dec_title.paragraph_format.space_after = Pt(24)
    r_dec_title = p_dec_title.add_run("CANDIDATE'S DECLARATION")
    r_dec_title.bold = True
    r_dec_title.font.name = "Times New Roman"
    r_dec_title.font.size = Pt(15)

    add_p(
        doc,
        "I hereby declare that the project work presented in this report entitled 'AI-ASSISTED HEALTH-RELATED MISINFORMATION "
        "VERIFICATION SYSTEM' submitted to the Department of Computer Science and Engineering, [COLLEGE NAME], is an authentic record "
        "of my own work carried out under the guidance of [PROJECT GUIDE NAME], [DESIGNATION], Department of Computer Science and Engineering."
    )

    add_p(
        doc,
        "I further declare that this report has not been submitted previously in part or in full to any other University or Institution "
        "for the award of any academic degree, diploma, or certificate. All literature, research papers, open-source datasets, and software "
        "libraries referenced in this work have been properly acknowledged and cited in accordance with standard academic guidelines."
    )

    p_dec_sig = doc.add_paragraph()
    p_dec_sig.paragraph_format.space_before = Pt(60)
    p_dec_sig.paragraph_format.line_spacing = 1.3
    r_dec_sig = p_dec_sig.add_run(
        "Place: [CITY / CAMPUS LOCATION]\n"
        "Date:  [SUBMISSION DATE]\n\n\n"
        "_____________________________________\n"
        "[STUDENT NAME]\n"
        "Register Number: [STUDENT REGISTER NUMBER]\n"
        "Department of Computer Science and Engineering\n"
        "[COLLEGE NAME]"
    )
    r_dec_sig.font.name = "Times New Roman"
    r_dec_sig.font.size = Pt(11)

    # -------------------------------------------------------------
    # 4. ACKNOWLEDGEMENT
    # -------------------------------------------------------------
    doc.add_page_break()
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(24)
    p_ack_title.paragraph_format.space_after = Pt(24)
    r_ack_title = p_ack_title.add_run("ACKNOWLEDGEMENT")
    r_ack_title.bold = True
    r_ack_title.font.name = "Times New Roman"
    r_ack_title.font.size = Pt(15)

    add_p(
        doc,
        "First and foremost, I express my profound gratitude to the Almighty for bestowing the strength, perseverance, and knowledge "
        "needed to successfully complete this academic endeavor."
    )

    add_p(
        doc,
        "I express my heartfelt and sincere gratitude to my respected Project Guide, [PROJECT GUIDE NAME], [DESIGNATION], Department of "
        "Computer Science and Engineering, for their invaluable guidance, constant encouragement, insightful suggestions, and thorough "
        "mentorship throughout the development of this project. Their continuous constructive critique played an essential role in shaping "
        "the architecture and evaluation rigor of this verification system."
    )

    add_p(
        doc,
        "I extend my deep gratitude to [HOD NAME], Head of the Department of Computer Science and Engineering, for providing the necessary "
        "academic facilities, computational infrastructure, and supportive environment throughout the duration of the course."
    )

    add_p(
        doc,
        "I also thank our respected Principal / Dean, [PRINCIPAL NAME], for providing administrative leadership and academic resources. "
        "I am grateful to all the faculty and laboratory staff members of the Department of Computer Science and Engineering for their direct "
        "and indirect assistance."
    )

    add_p(
        doc,
        "Lastly, I express my deepest love and gratitude to my family and friends, whose unending patience, moral encouragement, and personal "
        "sacrifices have been my enduring source of motivation."
    )

    # -------------------------------------------------------------
    # 5. ABSTRACT
    # -------------------------------------------------------------
    doc.add_page_break()
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(24)
    p_abs_title.paragraph_format.space_after = Pt(20)
    r_abs_title = p_abs_title.add_run("ABSTRACT")
    r_abs_title.bold = True
    r_abs_title.font.name = "Times New Roman"
    r_abs_title.font.size = Pt(15)

    add_p(
        doc,
        "The proliferation of unverified health assertions across social networks and digital platforms poses severe hazards to public "
        "well-being. Misleading claims concerning diseases, unauthorized therapies, and pharmaceutical efficacy often spread rapidly before "
        "qualified medical professionals can publish authoritative refutations. While modern generative Large Language Models (LLMs) can "
        "produce fluent conversational responses, their tendency to hallucinate unsupported medical statements and their lack of verifiable "
        "source citations make them unsuitable as unsupervised truth adjudicators in safety-critical domains."
    )

    add_p(
        doc,
        "To address these limitations, this project presents the 'AI-Assisted Health-Related Misinformation Verification System', a "
        "deterministic, multi-stage, evidence-grounded verification framework that eliminates unconstrained text generation from the truth "
        "determination process. The system retrieves candidate evidence from two complementary authoritative repositories: accredited journalistic "
        "fact-checking organizations via the Google Fact Check Tools API and peer-reviewed biomedical literature via the NCBI PubMed E-Utilities API. "
        "To ensure precise candidate filtering, the system implements domain-tailored neural re-ranking: a Sentence-BERT (SBERT) bi-encoder "
        "(all-MiniLM-L6-v2) for claim reviews and a deep MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder) pre-trained on 255 million PubMed "
        "query-article pairs for scientific abstracts."
    )

    add_p(
        doc,
        "The Top-10 ranked documents from each source stream undergo directional stance classification using a large pre-trained Natural "
        "Language Inference (NLI) model (cross-encoder/nli-deberta-v3-large) under an uncontaminated premise formulation. The resulting stance "
        "distributions (entailment, contradiction, and neutral) are synthesized by a deterministic decision engine enforcing a contradiction-precedent "
        "safety hierarchy. Evaluated on an expanded benchmark of 60 rigorous test claims (combining curated public health claims and gold SciFact "
        "biomedical instances), the system achieved an overall classification accuracy of 83.33%, a macro F1-score of 78.52%, and a weighted F1-score "
        "of 83.00%, outperforming the standard SBERT semantic similarity baseline (46.67% accuracy) by +36.66% absolute gain. On the SciFact biomedical "
        "retrieval benchmark, MedCPT demonstrated perfect top-rank retrieval with a Mean Reciprocal Rank (MRR) of 1.0000. All findings are rendered "
        "within an interactive Streamlit web dashboard featuring full citation traceability to PubMed identifiers (PMIDs) and verified URLs, "
        "enabling everyday users to easily check online health advice."
    )

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(6)
    r_kw_bold = p_kw.add_run("Keywords: ")
    r_kw_bold.bold = True
    r_kw_bold.font.name = "Times New Roman"
    r_kw_bold.font.size = Pt(11)
    r_kw = p_kw.add_run(
        "Health Misinformation, Natural Language Inference, MedCPT Cross-Encoder, Biomedical Information Retrieval, Sentence-BERT, Decision Engine."
    )
    r_kw.font.name = "Times New Roman"
    r_kw.font.size = Pt(11)

    # -------------------------------------------------------------
    # 6. TABLE OF CONTENTS
    # -------------------------------------------------------------
    doc.add_page_break()
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(24)
    p_toc_title.paragraph_format.space_after = Pt(18)
    r_toc_title = p_toc_title.add_run("TABLE OF CONTENTS")
    r_toc_title.bold = True
    r_toc_title.font.name = "Times New Roman"
    r_toc_title.font.size = Pt(15)

    toc_entries = [
        ("BONAFIDE CERTIFICATE", "ii"),
        ("CANDIDATE'S DECLARATION", "iii"),
        ("ACKNOWLEDGEMENT", "iv"),
        ("ABSTRACT", "v"),
        ("LIST OF FIGURES", "vii"),
        ("LIST OF TABLES", "viii"),
        ("LIST OF ABBREVIATIONS", "ix"),
        ("CHAPTER 1 – INTRODUCTION", "1"),
        ("    1.1 Introduction", "1"),
        ("    1.2 Background of the Project", "3"),
        ("    1.3 Problem Statement", "5"),
        ("    1.4 Objectives of the Project", "6"),
        ("    1.5 Motivation for the Project", "7"),
        ("        1.5.1 Increasing Availability of Online Health Information", "7"),
        ("        1.5.2 Difficulty of Manual Fact-Checking", "8"),
        ("        1.5.3 Need for Semantic Understanding", "9"),
        ("        1.5.4 Importance of Evidence-Based Verification", "10"),
        ("        1.5.5 Need for Objective Performance Measurement", "11"),
        ("    1.6 Scope of the Project", "12"),
        ("    1.7 Significance of the Project", "13"),
        ("    1.8 Organization of the Report", "15"),
        ("CHAPTER 2 – LITERATURE REVIEW", "16"),
        ("    2.1 Introduction", "16"),
        ("    2.2 Review of Related Research Papers", "17"),
        ("    2.3 Comparison of Existing Methods", "23"),
        ("    2.4 Research Gap", "25"),
        ("    2.5 Chapter Summary", "27"),
        ("CHAPTER 3 – SYSTEM DESIGN", "28"),
        ("    3.1 Introduction", "28"),
        ("    3.2 Existing System and Its Limitations", "28"),
        ("    3.3 Proposed System Architecture", "30"),
        ("    3.4 System Requirements Specification", "32"),
        ("        3.4.1 Functional Requirements", "32"),
        ("        3.4.2 Non-Functional Requirements", "33"),
        ("    3.5 System Architecture Diagram & Layers", "34"),
        ("    3.6 Module Description", "36"),
        ("    3.7 Data Flow Diagram (DFD)", "38"),
        ("    3.8 End-to-End System Workflow", "40"),
        ("    3.9 Decision-Making Logic & Canonical Verdicts", "41"),
        ("    3.10 Use Case Diagram", "43"),
        ("    3.11 Design Considerations & Engineering Constraints", "44"),
        ("    3.12 Chapter Summary", "46"),
        ("CHAPTER 4 – IMPLEMENTATION", "47"),
        ("    4.1 Introduction", "47"),
        ("    4.2 Technologies and Software Libraries Used", "47"),
        ("    4.3 Development Environment and Hardware Setup", "49"),
        ("    4.4 Claim Ingestion and Preprocessing", "50"),
        ("    4.5 Google Fact Check Tools API Integration", "51"),
        ("    4.6 PubMed Biomedical Retrieval Subsystem", "52"),
        ("    4.7 SBERT Bi-Encoder Ranking Implementation", "54"),
        ("    4.8 MedCPT Cross-Encoder Ranking Implementation", "55"),
        ("    4.9 Natural Language Inference Stance Classifier", "57"),
        ("    4.10 Multi-Source Deterministic Decision Engine", "59"),
        ("    4.11 User Interface & Provenance Presentation", "61"),
        ("    4.12 Error Handling and System Resilience", "63"),
        ("    4.13 Testing and Evaluation Subsystem Implementation", "64"),
        ("    4.14 Testing Procedures (Unit, Integration, Fallbacks)", "66"),
        ("    4.15 Implementation Limitations", "67"),
        ("    4.16 Chapter Summary", "68"),
        ("CHAPTER 5 – RESULTS AND DISCUSSION", "69"),
        ("    5.1 Introduction", "69"),
        ("    5.2 Evaluation Dataset Description (N=60)", "69"),
        ("    5.3 Evaluation Methodology & Protocol", "71"),
        ("    5.4 Level 1 NLI Classification Performance Results", "72"),
        ("    5.5 Level 2 Decision Engine Verdict Evaluation", "75"),
        ("    5.6 Information Retrieval Ranking Evaluation (SciFact)", "76"),
        ("    5.7 Comparison Against Baseline System", "78"),
        ("    5.8 Document Retrieval and Deduplication Analysis", "79"),
        ("    5.9 Error Analysis and Failure Case Examination", "81"),
        ("    5.10 Discussion of Key Findings", "83"),
        ("    5.11 Threats to Validity and Experimental Limitations", "85"),
        ("    5.12 Chapter Summary", "86"),
        ("CHAPTER 6 – CONCLUSION AND FUTURE WORK", "87"),
        ("    6.1 Conclusion", "87"),
        ("    6.2 Key Contributions of the Project", "88"),
        ("    6.3 Technical and Practical Limitations", "89"),
        ("    6.4 Future Work and Research Directions", "90"),
        ("REFERENCES", "92"),
        ("APPENDIX A: KEY SOURCE CODE REPOSITORY STRUCTURE", "95"),
        ("APPENDIX B: EVALUATION BENCHMARK DATASET SAMPLE", "97"),
        ("APPENDIX C: SAMPLE END-TO-END VERIFICATION PAYLOAD", "99"),
        ("APPENDIX D: REPRODUCIBILITY & USER EXECUTION GUIDE", "101"),
    ]

    t_toc = doc.add_table(rows=len(toc_entries), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    for idx, (title, page) in enumerate(toc_entries):
        cell_t = t_toc.cell(idx, 0)
        cell_p = t_toc.cell(idx, 1)
        cell_t.width = Inches(5.8)
        cell_p.width = Inches(0.7)
        set_cell_margins(cell_t, top=40, bottom=40, left=60, right=60)
        set_cell_margins(cell_p, top=40, bottom=40, left=60, right=60)
        
        pt = cell_t.paragraphs[0]
        pt.paragraph_format.line_spacing = 1.15
        pt.paragraph_format.space_after = Pt(1)
        rt = pt.add_run(title)
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(10.5)
        if "CHAPTER" in title or "APPENDIX" in title or "REFERENCES" in title or not title.startswith(" "):
            rt.bold = True

        pp = cell_p.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pp.paragraph_format.line_spacing = 1.15
        pp.paragraph_format.space_after = Pt(1)
        rp = pp.add_run(page)
        rp.font.name = "Times New Roman"
        rp.font.size = Pt(10.5)

    # -------------------------------------------------------------
    # 7. LIST OF FIGURES
    # -------------------------------------------------------------
    doc.add_page_break()
    p_lof_title = doc.add_paragraph()
    p_lof_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_title.paragraph_format.space_before = Pt(24)
    p_lof_title.paragraph_format.space_after = Pt(18)
    r_lof_title = p_lof_title.add_run("LIST OF FIGURES")
    r_lof_title.bold = True
    r_lof_title.font.name = "Times New Roman"
    r_lof_title.font.size = Pt(15)

    figures = [
        ("Figure 3.1", "Overall Multi-Stage Verification System Architecture", "35"),
        ("Figure 3.2", "Level 1 Data Flow Diagram (DFD) of System Processing", "39"),
        ("Figure 3.3", "Use Case Diagram for Verification Application & Public User Workflows", "43"),
        ("Figure 3.4", "Architecture Comparison: SBERT Bi-Encoder vs MedCPT Cross-Encoder", "56"),
        ("Figure 3.5", "Natural Language Inference (NLI) Stance Classification Architecture", "58"),
        ("Figure 3.6", "Decision Engine Contradiction-Precedent Adjudication Flowchart", "60"),
        ("Figure 5.1", "Level 1 NLI Stance Classification Confusion Matrix Heatmap (N = 60)", "74"),
        ("Figure 5.2", "Verification Pipeline Accuracy vs SBERT Similarity Baseline Comparison", "78"),
    ]

    t_lof = doc.add_table(rows=len(figures) + 1, cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(
        t_lof,
        [Inches(1.2), Inches(4.6), Inches(0.7)],
        ["Figure No.", "Title / Description", "Page"],
        [[f[0], f[1], f[2]] for f in figures],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT]
    )

    # -------------------------------------------------------------
    # 8. LIST OF TABLES
    # -------------------------------------------------------------
    doc.add_page_break()
    p_lot_title = doc.add_paragraph()
    p_lot_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_title.paragraph_format.space_before = Pt(24)
    p_lot_title.paragraph_format.space_after = Pt(18)
    r_lot_title = p_lot_title.add_run("LIST OF TABLES")
    r_lot_title.bold = True
    r_lot_title.font.name = "Times New Roman"
    r_lot_title.font.size = Pt(15)

    tables = [
        ("Table 2.1", "Comparative Analysis of Relevant Models and Research Approaches", "24"),
        ("Table 3.1", "Functional Requirements Specification Matrix", "33"),
        ("Table 3.2", "Canonical Verdict Category Definitions and Operational Semantics", "42"),
        ("Table 4.1", "Software Libraries, Frameworks, and Core Dependencies", "48"),
        ("Table 4.2", "System Retrieval Ceilings, Query Limits, and Deduplication Rules", "53"),
        ("Table 5.1", "Level 1 NLI Stance Classification Performance Breakdown (N = 60)", "73"),
        ("Table 5.2", "MedCPT Cross-Encoder Document Ranking Performance on SciFact", "76"),
        ("Table 5.3", "Overall Performance Comparison: Full Pipeline vs Baseline System", "78"),
        ("Table 5.4", "Document Retrieval Throughput, Deduplication Counts, and Latency", "80"),
    ]

    t_lot = doc.add_table(rows=len(tables) + 1, cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(
        t_lot,
        [Inches(1.2), Inches(4.6), Inches(0.7)],
        ["Table No.", "Title / Description", "Page"],
        [[t[0], t[1], t[2]] for t in tables],
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT]
    )

    # -------------------------------------------------------------
    # 9. LIST OF ABBREVIATIONS
    # -------------------------------------------------------------
    doc.add_page_break()
    p_abbr_title = doc.add_paragraph()
    p_abbr_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abbr_title.paragraph_format.space_before = Pt(24)
    p_abbr_title.paragraph_format.space_after = Pt(18)
    r_abbr_title = p_abbr_title.add_run("LIST OF ABBREVIATIONS")
    r_abbr_title.bold = True
    r_abbr_title.font.name = "Times New Roman"
    r_abbr_title.font.size = Pt(15)

    abbreviations = [
        ("AI", "Artificial Intelligence"),
        ("API", "Application Programming Interface"),
        ("BERT", "Bidirectional Encoder Representations from Transformers"),
        ("Bi-Encoder", "Two-tower neural architecture encoding sequences independently"),
        ("CDC", "Centers for Disease Control and Prevention"),
        ("CLS", "Classification Token in Transformer architectures"),
        ("Cross-Encoder", "Joint sequence neural architecture encoding pair sequences with cross-attention"),
        ("DeBERTa", "Decoding-enhanced BERT with Disentangled Attention"),
        ("DFD", "Data Flow Diagram"),
        ("DOI", "Digital Object Identifier"),
        ("E-Utilities", "Entrez Programming Utilities API provided by NCBI"),
        ("F1", "Harmonic mean of Precision and Recall (F1-score)"),
        ("GFC", "Google Fact Check Tools API"),
        ("IFCN", "International Fact-Checking Network"),
        ("IR", "Information Retrieval"),
        ("JSON", "JavaScript Object Notation"),
        ("LLM", "Large Language Model"),
        ("MedCPT", "Medical Contrastive Pre-trained Transformers"),
        ("MEDLINE", "Medical Literature Analysis and Retrieval System Online"),
        ("MRR", "Mean Reciprocal Rank"),
        ("NCBI", "National Center for Biotechnology Information"),
        ("NDCG", "Normalized Discounted Cumulative Gain"),
        ("NLM", "National Library of Medicine"),
        ("NLI", "Natural Language Inference"),
        ("NLP", "Natural Language Processing"),
        ("P@K", "Precision at Rank Cut-off K"),
        ("PMID", "PubMed Identifier"),
        ("PubMed", "Free biomedical bibliographic search engine by NLM"),
        ("R@K", "Recall at Rank Cut-off K"),
        ("REST", "Representational State Transfer"),
        ("SBERT", "Sentence-BERT"),
        ("SEP", "Separator Token in Transformer architectures"),
        ("UI", "User Interface"),
        ("URI", "Uniform Resource Identifier"),
        ("URL", "Uniform Resource Locator"),
        ("WHO", "World Health Organization"),
        ("XML", "Extensible Markup Language"),
    ]

    t_abbr = doc.add_table(rows=len(abbreviations) + 1, cols=2)
    t_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(
        t_abbr,
        [Inches(1.8), Inches(4.7)],
        ["Abbreviation / Term", "Expanded Form / Definition"],
        [[a[0], a[1]] for a in abbreviations],
        [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )

def build_chapter_1(doc):
    add_heading_1(doc, "CHAPTER 1 – INTRODUCTION")

    add_heading_2(doc, "1.1 Introduction")
    add_p(
        doc,
        "Today, almost everyone turns to the internet when they have questions about their health. Whenever people feel unwell, "
        "experience common symptoms, or want advice on diet, fitness, and home remedies, they routinely search online or read posts "
        "on social media platforms like WhatsApp, YouTube, and Facebook. Along with helpful advice, however, a large amount of false "
        "and misleading health information spreads online every single day. Everyday users frequently encounter viral posts claiming "
        "that simple kitchen ingredients can cure serious conditions like asthma or diabetes, or rumors warning people against safe "
        "medicines and vaccines. Believing these false claims can be very dangerous. An ordinary person might stop taking the medicines "
        "prescribed by their doctor, delay visiting a hospital during an emergency, or try untested home mixtures that could harm their health."
    )
    add_p(
        doc,
        "For an everyday person, figuring out whether an online health tip is true or false is very difficult. Most scientific research "
        "papers are written using complicated medical language, doctor terminology, and complex statistical figures that only healthcare "
        "specialists can easily understand. At the same time, simple internet searches often show conflicting blog posts, sponsored "
        "advertisements, and unverified personal opinions, leaving regular people confused about what to trust. Ordinary people simply "
        "do not have the time or specialized background knowledge to read through dense clinical studies just to check if a simple health "
        "tip they heard from a friend or saw in a family group chat is safe and accurate."
    )
    add_p(
        doc,
        "To solve this problem and help the general public, this project introduces the 'AI-Assisted Health-Related Misinformation "
        "Verification System'. This system is an easy-to-use tool designed specifically for ordinary people who want a fast, simple, and "
        "reliable way to check health claims they see online. When a user enters a question or claim—such as 'Does ginger tea cure asthma?'—the "
        "system automatically searches two trusted sources: verified fact-checking records (like Snopes and Health Feedback) and reliable medical "
        "research from PubMed. The system uses artificial intelligence to compare the meaning of the claim with the evidence, checks whether "
        "scientific findings agree with or disprove the claim, and gives the user a clear and simple result, such as 'Potentially supported', "
        "'Potentially refuted', or 'Insufficient evidence'. By providing straightforward explanations and direct links to trusted sources, "
        "the system helps regular people make safer, better-informed health choices."
    )

    add_callout(
        doc,
        "Core Design Principle: The verification system deliberately excludes unconstrained generative text models from the truth adjudication "
        "loop. Final verdicts are produced strictly through deterministic aggregation rules applied over calibrated cross-attention inference "
        "probabilities and peer-reviewed literature citations.",
        bold_prefix="SAFETY PRINCIPLE: "
    )

    add_heading_2(doc, "1.2 Background of the Project")
    add_p(
        doc,
        "Automated fact-checking has evolved substantially over the past decade. Early verification tools relied heavily on basic keyword "
        "filtering and lexical matching against small, static databases of debunked myths. While lexical methods execute quickly, they are "
        "fundamentally incapable of understanding linguistic variations, synonyms, or contextual negations. For example, a search for the "
        "claim 'Vitamin C prevents COVID-19' against a document containing 'Clinical trials show Vitamin C does not prevent COVID-19' would "
        "return a false-positive lexical match because the major keywords overlap, despite the fact that the document directly refutes the assertion."
    )
    add_p(
        doc,
        "With the emergence of deep learning and transformer-based language representations such as BERT, Natural Language Processing (NLP) "
        "systems gained the ability to capture semantic meaning. Researchers introduced Natural Language Inference (NLI) frameworks, which "
        "model the relationship between a premise text and a hypothesis text into three distinct categories: entailment (the premise supports "
        "the hypothesis), contradiction (the premise refutes the hypothesis), or neutral (the premise provides neither sufficient support "
        "nor refutation)."
    )
    add_p(
        doc,
        "In the biomedical domain, verifying assertions requires consulting primary scientific evidence. The National Center for Biotechnology "
        "Information (NCBI) hosts the PubMed database, which indexes over 36 million citations from MEDLINE, life science journals, and online "
        "books. In parallel, global fact-checking organizations (such as Health Feedback, Snopes, PolitiFact, and Full Fact) adhere to the "
        "standards of the International Fact-Checking Network (IFCN) and publish structured claim reviews indexed by the Google Fact Check Tools API. "
        "The background of this project lies in bridging these two distinct knowledge streams: journalistic fact-checking for viral claims and "
        "peer-reviewed biomedical research for deep clinical authority."
    )

    add_heading_2(doc, "1.3 Problem Statement")
    add_p(
        doc,
        "Manual verification of health claims is labor-intensive, time-consuming, and incapable of scaling to the velocity of digital "
        "misinformation. Conversely, naive automated approaches introduce critical safety hazards:"
    )
    add_numbered_item(
        doc, "1",
        "Keyword-Based Search Failures: Simple search engines retrieve documents containing matching keywords regardless of whether the "
        "document supports, refutes, or simply mentions the condition in an unrelated context.",
        bold_prefix="Lexical Matching Fragility: "
    )
    add_numbered_item(
        doc, "2",
        "Generative LLM Hallucinations: General-purpose conversational models (e.g., ChatGPT, Llama) generate plausible-sounding text but "
        "routinely hallucinate nonexistent medical studies, invent citations, and produce conflicting verdicts depending on subtle prompt variations.",
        bold_prefix="Ungrounded Hallucinations: "
    )
    add_numbered_item(
        doc, "3",
        "Absence of Provenance: Existing public chatbots fail to provide direct, immutable links to primary scientific literature, making it "
        "impossible for clinicians or users to verify where the generated guidance originated.",
        bold_prefix="Lack of Verifiable Provenance: "
    )
    add_numbered_item(
        doc, "4",
        "Unreliable Evaluation Metrics: Prior systems frequently suffer from premise contamination during evaluation (concatenating the claim into "
        "the evidence premise) or lack standard classification metrics (Macro/Weighted Precision, Recall, F1, and IR ranking metrics), obscuring real performance.",
        bold_prefix="Evaluation Deficiencies: "
    )
    add_p(
        doc,
        "The problem addressed by this project is the lack of an integrated, auditable, and mathematically grounded verification system that "
        "couples multi-source evidence retrieval with specialized biomedical ranking, directional NLI stance analysis, and deterministic "
        "decision-making, supported by a reproducible quantitative evaluation module."
    )

    add_heading_2(doc, "1.4 Objectives of the Project")
    add_p(
        doc,
        "The primary objective of this project is to build, integrate, and evaluate an AI-Assisted Health-Related Misinformation Verification "
        "System that accurately verifies health assertions against authoritative external repositories. The specific objectives include:"
    )
    add_numbered_item(
        doc, "1",
        "Dual-Source Knowledge Ingestion: Develop automated retrieval connectors for both the Google Fact Check Tools API (journalistic reviews) "
        "and the NCBI PubMed E-Utilities API (peer-reviewed scientific literature), implementing multi-query expansion and deduplication ceilings.",
        bold_prefix="Multi-Source Retrieval: "
    )
    add_numbered_item(
        doc, "2",
        "Specialized Two-Tier Neural Re-Ranking: Implement a Sentence-BERT (SBERT) bi-encoder (all-MiniLM-L6-v2) for fact-checking summaries and "
        "a deep MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder) pre-trained on 255M PubMed query-article pairs for biomedical abstracts.",
        bold_prefix="Domain-Specific Re-Ranking: "
    )
    add_numbered_item(
        doc, "3",
        "Directional Stance Inference: Integrate a large transformer-based NLI model (cross-encoder/nli-deberta-v3-large) to compute 3-way "
        "directional stance probabilities (entailment, contradiction, neutral) under an uncontaminated premise formulation.",
        bold_prefix="NLI Stance Classification: "
    )
    add_numbered_item(
        doc, "4",
        "Deterministic Decision Adjudication: Construct a rule-based decision engine enforcing a contradiction-precedent safety hierarchy to "
        "map multi-source evidence tallies into four canonical verdicts: Potentially supported, Potentially refuted, Mixed evidence, and Insufficient evidence.",
        bold_prefix="Safe Decision Adjudication: "
    )
    add_numbered_item(
        doc, "5",
        "Interactive Clinical Dashboard: Build an accessible Streamlit web application displaying top-level verdicts, risk banners, transparent reasoning "
        "chains, and evidence cards with direct hyperlinks to PubMed identifiers (PMIDs) and verified fact-check sources.",
        bold_prefix="Transparent User Interface: "
    )
    add_numbered_item(
        doc, "6",
        "Rigorous Multi-Tier Evaluation: Implement an evaluation subsystem calculating Accuracy, Macro/Weighted Precision, Recall, F1-scores, "
        "Confusion Matrices, and Information Retrieval ranking metrics (MRR, NDCG@K) on an expanded 60-example benchmark combining Public Health and SciFact datasets.",
        bold_prefix="Empirical Evaluation: "
    )

    add_heading_2(doc, "1.5 Motivation for the Project")
    add_p(
        doc,
        "The motivation behind this project arises from multiple urgent societal and technological factors:"
    )
    add_heading_3(doc, "1.5.1 Increasing Availability of Online Health Information")
    add_p(
        doc,
        "Over 70% of internet users report searching for health and wellness information online. Unfortunately, search engine optimization (SEO) "
        "and algorithmic engagement incentives frequently elevate sensational, inaccurate, or commercially motivated medical claims over sober, "
        "peer-reviewed scientific conclusions. This creates an infodemic that endangers vulnerable populations."
    )
    add_heading_3(doc, "1.5.2 Difficulty of Manual Fact-Checking")
    add_p(
        doc,
        "Fact-checking a single medical claim requires hours of expert literature searching, statistical analysis of clinical trials, and synthesis "
        "of contradictory trial results. The volume of health assertions generated daily far exceeds the capacity of human fact-checkers, making "
        "intelligent computational verification assistance an urgent necessity."
    )
    add_heading_3(doc, "1.5.3 Need for Semantic Understanding")
    add_p(
        doc,
        "Medical terminology is dense and heavily synonymous. A claim regarding 'high blood pressure' must be recognized as semantically identical "
        "to 'hypertension'. Furthermore, syntactic negation ('not effective') fundamentally reverses truth value. Deep semantic representation "
        "and cross-attention transformers are required to capture these linguistic dynamics accurately."
    )
    add_heading_3(doc, "1.5.4 Importance of Evidence-Based Verification")
    add_p(
        doc,
        "In healthcare, a verdict cannot be trusted on authority alone; it must be backed by transparent, reproducible evidence. Providing "
        "provenance citations (PMID, journal name, publication year) empowers clinicians, journalists, and citizens to inspect the primary "
        "literature directly, fostering epistemic trust."
    )
    add_heading_3(doc, "1.5.5 Need for Objective Performance Measurement")
    add_p(
        doc,
        "Many commercial verification prototypes rely on subjective evaluations or self-reported accuracy. A robust academic project must "
        "measure performance using mathematically rigorous metrics, test against gold-standard scientific benchmarks such as SciFact, and "
        "compare against established baselines under identical operational constraints."
    )

    add_heading_2(doc, "1.6 Scope of the Project")
    add_p(
        doc,
        "The scope of this project encompasses the design, implementation, and empirical evaluation of a software-based verification system. "
        "The concrete boundaries of the project are defined as follows:"
    )
    add_bullet_item(doc, "English-language health, dietary, pharmaceutical, and epidemiological claims submitted in natural language text.", bold_prefix="Claim Domain: ")
    add_bullet_item(doc, "Automated query dispatching to the Google Fact Check Tools API and NCBI PubMed E-Utilities API.", bold_prefix="Retrieval Sources: ")
    add_bullet_item(doc, "Candidate ranking using Sentence-BERT (all-MiniLM-L6-v2) and MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder).", bold_prefix="Neural Ranking Models: ")
    add_bullet_item(doc, "Premise-hypothesis stance analysis using cross-encoder/nli-deberta-v3-large.", bold_prefix="Inference Engine: ")
    add_bullet_item(doc, "Rule-based deterministic adjudication mapping evidence counts into four canonical verdict categories.", bold_prefix="Decision Rules: ")
    add_bullet_item(doc, "Interactive presentation via Streamlit with full citation traceability and offline evaluation support.", bold_prefix="Delivery Interface: ")
    add_bullet_item(doc, "Explicit Non-Scope: The system is NOT a diagnostic medical tool, does not prescribe treatments, and does not replace professional clinical consultations.", bold_prefix="Clinical Boundary: ")

    add_heading_2(doc, "1.7 Significance of the Project")
    add_p(
        doc,
        "The significance of this project lies in its methodological conservatism and transparency. By refusing to delegate truth determination "
        "to a generative LLM, the system eliminates hallucination risks at the architectural level. By pairing fast journalistic fact-checks with "
        "deep MEDLINE peer-reviewed literature, the system bridges the gap between emerging public rumors and established scientific consensus. "
        "Furthermore, the project provides an open, reproducible evaluation harness that enables future researchers to benchmark new biomedical "
        "retrieval and inference models systematically."
    )

    add_heading_2(doc, "1.8 Organization of the Report")
    add_p(
        doc,
        "This project report is organized into six comprehensive chapters, followed by references and appendices:"
    )
    add_bullet_item(doc, "Chapter 1 – Introduction: Presents the background, problem statement, objectives, motivation, scope, and significance.", bold_prefix="Chapter 1: ")
    add_bullet_item(doc, "Chapter 2 – Literature Review: Reviews five to eight authoritative research papers on SBERT, MedCPT, DeBERTa, SciFact, and fact-checking, accompanied by a comparative table and research gap analysis.", bold_prefix="Chapter 2: ")
    add_bullet_item(doc, "Chapter 3 – System Design: Details the functional and non-functional requirements, architectural layers, DFDs, use case diagrams, decision flowcharts, and unified data schemas.", bold_prefix="Chapter 3: ")
    add_bullet_item(doc, "Chapter 4 – Implementation: Explains the concrete software technologies, APIs, document retrieval limits, SBERT/MedCPT ranking algorithms, NLI inference, UI design, error handling, and unit test suites.", bold_prefix="Chapter 4: ")
    add_bullet_item(doc, "Chapter 5 – Results and Discussion: Reports empirical evaluation results on the expanded 60-claim benchmark, including Accuracy, Macro/Weighted F1, Confusion Matrices, SciFact IR ranking metrics, baseline comparisons, and error analyses.", bold_prefix="Chapter 5: ")
    add_bullet_item(doc, "Chapter 6 – Conclusion and Future Work: Summarizes the project findings, core contributions, architectural limitations, and prospective research directions.", bold_prefix="Chapter 6: ")
    add_bullet_item(doc, "References & Appendices: Provides genuine academic citations, source repository listings, benchmark dataset tables, and user execution instructions.", bold_prefix="Supplementary: ")

def build_chapter_2(doc):
    add_heading_1(doc, "CHAPTER 2 – LITERATURE REVIEW")

    add_heading_2(doc, "2.1 Introduction")
    add_p(
        doc,
        "Developing an automated verification system for health misinformation requires synthesizing research across multiple subfields of "
        "computer science and biomedical informatics: dense semantic text representation, domain-specific information retrieval, transformer-based "
        "natural language inference, and scientific claim verification benchmarks. This chapter reviews the seminal research publications that "
        "form the theoretical and practical foundation of our system, examines their methodologies and limitations, provides a structured "
        "comparative analysis, and identifies the practical research gap addressed by our architecture."
    )

    add_heading_2(doc, "2.2 Review of Related Research Papers")

    # Paper 1: SBERT
    add_heading_3(doc, "2.2.1 Paper 1: Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks (2019)")
    add_bullet_item(doc, "Nils Reimers and Iryna Gurevych.", bold_prefix="Authors: ")
    add_bullet_item(doc, "Conference on Empirical Methods in Natural Language Processing (EMNLP 2019).", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To develop a computationally efficient method for deriving semantically meaningful sentence embeddings that can be compared using cosine similarity.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The authors introduced a siamese and triplet network structure over pre-trained BERT and RoBERTa models. The architecture pools token representations to derive fixed-size vectors (e.g., 384 or 768 dimensions) and trains them on NLI datasets using classification and regression objective functions.", bold_prefix="Methodology: ")
    add_bullet_item(doc, "SBERT reduced the computational time required to find the most similar sentence pair in a collection of 10,000 sentences from 65 hours (using standard cross-encoder BERT) to approximately 5 milliseconds, while maintaining state-of-the-art semantic textual similarity (STS) benchmark accuracy.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "In our system, SBERT (specifically the all-MiniLM-L6-v2 variant) powers Module 2's fact-checking re-ranking stream. Because journalistic claim reviews are relatively concise, SBERT provides rapid dense semantic comparison between user claims and candidate reviews.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "Bi-encoders encode queries and documents independently without cross-attention. As a result, SBERT can overlook fine-grained token-level interactions, biological entity negations, and complex clinical dependencies present in long biomedical texts.", bold_prefix="Limitations: ")

    # Paper 2: MedCPT
    add_heading_3(doc, "2.2.2 Paper 2: MedCPT: Contrastive Pre-trained Transformers with Clinical PubMed Data (2023)")
    add_bullet_item(doc, "Qiao Jin, Bofei Liu, Sheng Zhang, Peng Shan, Ronald Leaman, Zhiyong Lu.", bold_prefix="Authors: ")
    add_bullet_item(doc, "Bioinformatics / National Center for Biotechnology Information (NCBI), NLM, NIH (arXiv:2307.00589).", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To construct domain-specific pre-trained foundation models tailored specifically for zero-shot biomedical information retrieval.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The authors leveraged an unprecedented training corpus of 255 million search log query-click pairs collected from the PubMed search engine. They developed a dual-model framework consisting of MedCPT Bi-Encoders and a deep MedCPT Cross-Encoder (ncbi/MedCPT-Cross-Encoder), fine-tuned using contrastive loss to capture deep biomedical semantics.", bold_prefix="Methodology: ")
    add_bullet_item(doc, "MedCPT established new state-of-the-art performance across all six benchmark datasets in the Biomedical Information Retrieval (BioASQ) and TREC-COVID retrieval evaluations, substantially outperforming general-domain encoders (such as Contriever and standard BERT) and clinical models like BioBERT.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "MedCPT Cross-Encoder serves as the primary re-ranking engine for scientific literature in Module 2 of our project. By computing all-to-all cross-attention between user claims and PubMed titles/abstracts, it accurately identifies relevant clinical evidence that bi-encoders miss.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "The cross-encoder architecture requires significant computational resources compared to bi-encoders, making it computationally prohibitive to rank thousands of candidate documents on CPU. This necessitates our two-tier filtering strategy where candidate PMIDs are restricted to 100 before cross-attention.", bold_prefix="Limitations: ")

    # Paper 3: DeBERTa
    add_heading_3(doc, "2.2.3 Paper 3: DeBERTa: Decoding-enhanced BERT with Disentangled Attention (2021)")
    add_bullet_item(doc, "Pengcheng He, Xiaodong Liu, Jianfeng Gao, Weizhu Chen.", bold_prefix="Authors: ")
    add_bullet_item(doc, "International Conference on Learning Representations (ICLR 2021).", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To improve transformer representations by separating content and relative positional encodings, and enhancing masked language decoding.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The authors introduced two architectural innovations: (1) a disentangled attention mechanism where each word is represented using two vectors (content and relative position), computing attention matrices over content-to-content, content-to-position, and position-to-content pairs; and (2) an enhanced mask decoder that incorporates absolute positions during token prediction.", bold_prefix="Methodology: ")
    add_bullet_item(doc, "DeBERTa significantly outperformed RoBERTa and ELECTRA across the GLUE and SuperGLUE benchmarks. When scaled to large architectures, it achieved human-level performance on the Multi-Genre Natural Language Inference (MNLI) benchmark.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "Module 3 utilizes cross-encoder/nli-deberta-v3-large to perform directional stance classification between retrieved evidence passages (premises) and user health claims (hypotheses), providing calibrated probabilities across entailment, contradiction, and neutral classes.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "Large DeBERTa models require substantial parameter memory (approx. 1.74 GB for deberta-v3-large) and exhibit higher inference latency on single-core CPU environments.", bold_prefix="Limitations: ")

    # Paper 4: SciFact
    add_heading_3(doc, "2.2.4 Paper 4: Fact or Fiction: Verifying Scientific Claims with SciFact (2020)")
    add_bullet_item(doc, "David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu Wang, Madeleine van Zuylen, Arman Cohan, Hannaneh Hajishirzi.", bold_prefix="Authors: ")
    add_bullet_item(doc, "Conference on Empirical Methods in Natural Language Processing (EMNLP 2020).", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To introduce a scientific claim verification benchmark based on expert-written claims paired with peer-reviewed research abstracts from PubMed.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The authors constructed the SciFact dataset, consisting of 1,409 expert-curated claims verified against 5,183 research abstracts with sentence-level evidence annotations and three truth labels (SUPPORT, CONTRADICT, NOINFO). They established baseline retrieval and pipeline evaluation protocols.", bold_prefix="Methodology: ")
    add_bullet_item(doc, "The study demonstrated that standard open-domain fact-checking models perform poorly on scientific claims due to domain mismatch, complex clinical conditions, and nuanced statistical reporting. Evidence retrieval was identified as the primary performance bottleneck.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "SciFact serves as our benchmark standard. In Section 5.6, we evaluate MedCPT's biomedical document retrieval capability directly against gold SciFact citation instances, verifying that our re-ranking engine successfully places primary scientific evidence at rank 1.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "SciFact claims are authored by biomedical experts with precise academic syntax, whereas real-world social media health claims often feature informal language, colloquialisms, and spelling ambiguities.", bold_prefix="Limitations: ")

    # Paper 5: FEVER
    add_heading_3(doc, "2.2.5 Paper 5: FEVER: A Large-scale Dataset for Fact Extraction and VERification (2018)")
    add_bullet_item(doc, "James Thorne, Andreas Vlachos, Christos Christodoulopoulos, Arpit Mittal.", bold_prefix="Authors: ")
    add_bullet_item(doc, "Annual Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2018).", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To provide a massive benchmark dataset and formal verification formulation for automated fact-checking.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The authors generated 185,445 claims based on Wikipedia articles, labeled through human annotation into Supported, Refuted, or NotEnoughInfo, requiring systems to retrieve verifiable evidence sentences.", bold_prefix="Methodology: ")
    add_bullet_item(doc, "FEVER established the standard three-stage architecture for automated fact-checking: (1) Document Retrieval, (2) Sentence/Evidence Selection, and (3) Stance/Truth Entailment Prediction.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "Our system's architectural pipeline directly follows the canonical FEVER three-stage paradigm, adapting it to the medical domain by introducing dual-source knowledge retrieval and deterministic contradiction-precedent aggregation.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "FEVER relies strictly on Wikipedia as its sole knowledge source. Wikipedia lacks the deep clinical trial rigor and peer-reviewed authority required to adjudicate life-or-death healthcare claims.", bold_prefix="Limitations: ")

    # Paper 6: NCBI E-Utilities
    add_heading_3(doc, "2.2.6 Paper 6: Entrez Programming Utilities Help: The E-Utilities API (2009)")
    add_bullet_item(doc, "Eric Sayers.", bold_prefix="Authors: ")
    add_bullet_item(doc, "National Center for Biotechnology Information (NCBI), National Library of Medicine (NLM), NIH.", bold_prefix="Publication Venue: ")
    add_bullet_item(doc, "To provide programmatic access to all Entrez life science databases, including PubMed, PMC, and GenBank.", bold_prefix="Research Objective: ")
    add_bullet_item(doc, "The documentation details the RESTful query architecture of E-Utilities, covering esearch (searching query terms to obtain UID lists), esummary (fetching brief document summaries), and efetch (retrieving full XML bibliographic and abstract records in batched calls).", bold_prefix="Methodology: ")
    add_bullet_item(doc, "Demonstrates how structured query parameters, rate limits (3 requests per second without API keys, 10 with keys), and batch fetching can retrieve thousands of biomedical citations efficiently.", bold_prefix="Key Findings: ")
    add_bullet_item(doc, "E-Utilities constitutes the foundational data ingestion pipeline of Module 1, retrieving authoritative PMIDs, publication years, journal titles, and full abstracts for all medical queries.", bold_prefix="Relevance to This Project: ")
    add_bullet_item(doc, "NCBI imposes strict rate limits and network latency constraints, requiring client applications to implement multi-query deduplication and single-batch XML requests to prevent service timeouts.", bold_prefix="Limitations: ")

    add_heading_2(doc, "2.3 Comparison of Existing Methods")
    add_p(
        doc,
        "Table 2.1 provides a structured comparative summary of existing models, architectures, and approaches relevant to automated "
        "claim verification."
    )

    t_comp = doc.add_table(rows=6, cols=5)
    format_table(
        t_comp,
        [Inches(1.3), Inches(1.1), Inches(1.4), Inches(1.4), Inches(1.3)],
        ["Model / Approach", "Primary Domain", "Architecture Type", "Key Strengths", "Core Limitations"],
        [
            ["Keyword Matching (BM25 / Lucene)", "General Text", "Lexical Inverted Index", "Extremely fast; zero GPU requirements; exact lexical hit.", "No semantic understanding; fails on synonyms; vulnerable to negation."],
            ["Sentence-BERT (Reimers et al., 2019)", "General Text", "Siamese Bi-Encoder (MiniLM)", "Fast dense vector search; scalable cosine similarity ranking.", "No token-level cross-attention; misses complex medical syntax."],
            ["MedCPT Cross-Encoder (Jin et al., 2023)", "Biomedical Literature", "Deep Cross-Encoder Transformer", "Trained on 255M PubMed queries; deep semantic relevance.", "Computationally heavy; cannot rank large corpora without pre-filtering."],
            ["DeBERTa-v3-large NLI (He et al., 2021)", "General NLI", "Disentangled Attention Transformer", "State-of-the-art directional stance inference on MNLI.", "Requires high memory; does not retrieve external evidence independently."],
            ["Conversational LLMs (GPT-4 / Llama 3)", "Open Domain", "Generative Decoder Transformer", "Fluent text generation; conversational interaction.", "Hallucinates nonexistent studies; no verifiable provenance citations."],
        ],
        [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    )

    p_cap_t1 = doc.add_paragraph()
    p_cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_t1.paragraph_format.space_before = Pt(4)
    p_cap_t1.paragraph_format.space_after = Pt(12)
    r_ct1 = p_cap_t1.add_run("Table 2.1: Comparative Analysis of Relevant Models and Research Approaches")
    r_ct1.font.name = "Times New Roman"
    r_ct1.font.size = Pt(10)
    r_ct1.bold = True

    add_heading_2(doc, "2.4 Research Gap")
    add_p(
        doc,
        "A rigorous synthesis of the reviewed literature reveals several critical research gaps in automated health claim verification:"
    )
    add_numbered_item(
        doc, "1",
        "Siloed Knowledge Sources: Most existing systems query either news fact-checking databases (which lack primary scientific authority) "
        "or biomedical literature (which rarely covers viral, colloquial conspiracy theories). There is a distinct absence of architectures "
        "that systematically triangulate journalistic claim reviews with primary peer-reviewed PubMed citations.",
        bold_prefix="Dual-Source Disconnect: "
    )
    add_numbered_item(
        doc, "2",
        "Source-Agnostic Ranking: Standard verification pipelines apply generic lexical algorithms (BM25) or generic dense encoders across all "
        "data types. Journalistic summaries require semantic similarity bi-encoders, whereas dense medical abstracts require deep biomedical cross-encoders.",
        bold_prefix="Inappropriate Single-Model Ranking: "
    )
    add_numbered_item(
        doc, "3",
        "The Hallucination Danger of Generative LLMs: Emerging healthcare AI tools increasingly utilize generative chat models to answer medical "
        "queries directly. When prompted with controversial health claims, these models frequently invent citations and produce conflicting verdicts. "
        "There is an urgent need for deterministic, rule-based decision architectures that treat evidence analysis as an auditable scientific process.",
        bold_prefix="Ungrounded Generative Adjudication: "
    )
    add_numbered_item(
        doc, "4",
        "Evaluation Flaws and Premise Contamination: Existing fact-checking evaluation scripts often suffer from subtle methodology flaws, such as "
        "concatenating the claim text into the retrieved evidence premise during testing. This introduces artificial premise contamination that falsely "
        "inflates model entailment accuracy to near 100% on contradiction claims.",
        bold_prefix="Flawed Evaluation Methodologies: "
    )

    add_heading_2(doc, "2.5 Chapter Summary")
    add_p(
        doc,
        "This chapter reviewed six genuine research publications spanning Sentence-BERT, MedCPT, DeBERTa, SciFact, FEVER, and NCBI E-Utilities. "
        "The comparative analysis demonstrated that while bi-encoders offer computational speed and cross-encoders provide deep semantic relevance, "
        "neither component is sufficient on its own. The identified research gaps motivate our proposed system: an integrated, multi-stage "
        "architecture that combines dual-source retrieval, domain-specific neural re-ranking, directional NLI stance classification, and deterministic "
        "decision rules with rigorous, uncontaminated performance evaluation."
    )

print("Preliminary pages, Chapter 1, and Chapter 2 generator module created.")
