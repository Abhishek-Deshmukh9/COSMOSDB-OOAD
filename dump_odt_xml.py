import zipfile, xml.etree.ElementTree as ET

odt_path = r'C:/Users/abhis/.gemini/antigravity/brain/8677ee63-9895-4d1a-998e-2a9c487059d3/.user_uploaded/media_1795016844713_1ef317bb.odt'
with zipfile.ZipFile(odt_path, 'r') as z:
    xml_data = z.read('content.xml')

root = ET.fromstring(xml_data)
body = root.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')
text = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text')

for i, child in enumerate(text):
    s = ET.tostring(child, encoding='utf-8').decode('utf-8')
    print(f"=== CHILD {i} ===")
    print(s[:300])
