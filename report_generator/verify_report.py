"""Verify the generated report has all expected content."""
import sys
sys.path.insert(0, r"c:\Users\abhis\Desktop\Pjts\OOAD\report_generator")
from docx import Document

doc = Document(r"c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB_OOAD_Report.docx")

# Count content
paragraphs = len(doc.paragraphs)
tables = len(doc.tables)
words = sum(len(p.text.split()) for p in doc.paragraphs)

# Count images
image_count = 0
for rel in doc.part.rels.values():
    if "image" in rel.reltype:
        image_count += 1

# Find figure references
figure_refs = set()
for p in doc.paragraphs:
    text = p.text
    for i in range(1, 20):
        if f"Figure {i}:" in text:
            figure_refs.add(i)

# Find pattern diagram references
pattern_figs = []
for p in doc.paragraphs:
    text = p.text
    for pattern in ["Builder Pattern", "Repository/Adapter Pattern", "Strategy Pattern", "Observer Pattern"]:
        if pattern in text and "Before vs. After" in text:
            pattern_figs.append(pattern)

print(f"Paragraphs: {paragraphs}")
print(f"Tables: {tables}")  
print(f"Words: {words}")
print(f"Embedded images: {image_count}")
print(f"Figure captions found: {sorted(figure_refs)}")
print(f"Pattern diagram captions: {pattern_figs}")
print(f"Pages (est): {words // 400}")
