"""
Master script to assemble the complete college project report for:
AI-ASSISTED HEALTH-RELATED MISINFORMATION VERIFICATION SYSTEM
Generates AI_Assisted_Health_Related_Misinformation_Verification_System_Report.docx
and exports to AI_Assisted_Health_Related_Misinformation_Verification_System_Report.pdf.
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from report_helpers import init_document, REPORT_DIR
from report_prelims_ch1_ch2 import build_preliminary_pages, build_chapter_1, build_chapter_2
from report_ch3_ch4 import build_chapter_3, build_chapter_4
from report_ch5_ch6_refs import build_chapter_5, build_chapter_6, build_references, build_appendices

DOCX_OUTPUT = REPORT_DIR / "AI_Assisted_Health_Related_Misinformation_Verification_System_Report.docx"

def main():
    print("=" * 70)
    print("BUILDING COMPLETE COLLEGE PROJECT REPORT")
    print("Project: AI-ASSISTED HEALTH-RELATED MISINFORMATION VERIFICATION SYSTEM")
    print("=" * 70)

    print("Step 1: Initializing document with Times New Roman & A4 formatting...")
    doc = init_document()

    print("Step 2: Building Preliminary Pages (Cover, Cert, Decl, Ack, Abstract, TOC, Figures, Tables, Abbreviations)...")
    build_preliminary_pages(doc)

    print("Step 3: Building Chapter 1 (Introduction)...")
    build_chapter_1(doc)

    print("Step 4: Building Chapter 2 (Literature Review)...")
    build_chapter_2(doc)

    print("Step 5: Building Chapter 3 (System Design)...")
    build_chapter_3(doc)

    print("Step 6: Building Chapter 4 (Implementation)...")
    build_chapter_4(doc)

    print("Step 7: Building Chapter 5 (Results and Discussion)...")
    build_chapter_5(doc)

    print("Step 8: Building Chapter 6 (Conclusion and Future Work)...")
    build_chapter_6(doc)

    print("Step 9: Building References...")
    build_references(doc)

    print("Step 10: Building Appendices...")
    build_appendices(doc)

    print(f"Step 11: Saving Word document to {DOCX_OUTPUT}...")
    doc.save(str(DOCX_OUTPUT))
    print(f"Successfully generated DOCX: {DOCX_OUTPUT.name} ({DOCX_OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
