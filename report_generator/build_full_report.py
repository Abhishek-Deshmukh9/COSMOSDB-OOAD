"""
build_full_report.py
Master Orchestration Script to generate the complete publication-ready
~24-page OOAD Case Study Report (COSMODB_OOAD_Report.docx).
"""
import os
import sys
import shutil

# Add report_generator directory to Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from report_style import create_report_document
from part1_front_and_sec1_to_4 import build_part1
from part2_sec5_to_6 import build_part2
from part3_sec7_to_8 import build_part3
from part4_sec9_to_15 import build_part4

def main():
    print("=" * 60)
    print("BUILDING COMPLETE OOAD CASE STUDY REPORT (CSE556)")
    print("=" * 60)

    diagrams_dir = os.path.join(CURRENT_DIR, "diagrams")
    print(f"Using Diagrams Directory: {diagrams_dir}")

    # 1. Initialize Document
    print("Initializing styled document (Times New Roman, 1-inch margins, 1.5 line spacing)...")
    doc = create_report_document()

    # 2. Build Part 1: Front Matter & Sections 1 to 4
    print("Assembling Part 1: Front Matter, Abstract, Intro/Lit Survey, Objectives, Object Basics...")
    build_part1(doc)

    # 3. Build Part 2: Sections 5 to 6 (UML Modeling & OO Analysis)
    print("Assembling Part 2: UML Modeling (Figures 1-7) & Object-Oriented Analysis (22 Nouns, 3 Use Cases)...")
    build_part2(doc, diagrams_dir)

    # 4. Build Part 3: Sections 7 to 8 (Design Principles, Corollaries, Patterns, Architecture)
    print("Assembling Part 3: Bahrami Corollaries, SOLID Audit, GoF Patterns (Builder, Strategy, Observer, Adapter), Figure 8...")
    build_part3(doc, diagrams_dir)

    # 5. Build Part 4: Sections 9 to 15 (Implementation, Results, Discussion, Conclusion, References, Appendices)
    print("Assembling Part 4: Implementation, Traceability Matrix, Discussion, References, Appendices A & B...")
    build_part4(doc)

    # 6. Save Report
    out_paths = [
        r"c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB_OOAD_Report.docx",
        r"c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\COSMODB_OOAD_Report.docx"
    ]

    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            doc.save(p)
            size_kb = os.path.getsize(p) / 1024
            print(f"Successfully generated: {p} ({size_kb:.1f} KB)")
        except PermissionError:
            print(f"[Warning] Could not overwrite {p} (file is currently locked/open in another application like Microsoft Word).")
        except Exception as e:
            print(f"[Warning] Error saving to {p}: {e}")

    print("=" * 60)
    print("REPORT GENERATION COMPLETE!")
    print(f"Total Paragraphs: {len(doc.paragraphs)}")
    print(f"Total Tables: {len(doc.tables)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
