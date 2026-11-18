import zipfile, xml.etree.ElementTree as ET, os

odt_path = r'C:/Users/abhis/.gemini/antigravity/brain/8677ee63-9895-4d1a-998e-2a9c487059d3/.user_uploaded/media_1795016844713_1ef317bb.odt'
with zipfile.ZipFile(odt_path, 'r') as z:
    xml_data = z.read('content.xml')

root = ET.fromstring(xml_data)
body = root.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')
text = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text')

for i, child in enumerate(text):
    tag = child.tag.split('}')[-1]
    txt = ''.join(child.itertext()).strip()
    frames = []
    for f in child.iter('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}frame'):
        fname = f.attrib.get('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}name', '')
        for img in f.iter('{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}image'):
            href = img.attrib.get('{http://www.w3.org/1999/xlink}href', '')
            frames.append((fname, href))
    if txt or frames:
        print(f"[{i}] {tag}: txt='{txt}' frames={frames}")
