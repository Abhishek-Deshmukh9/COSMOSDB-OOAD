import os, re

svg_dir = r'c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\docs\OOAD\diagrams'
for f in sorted(os.listdir(svg_dir)):
    if f.endswith('.svg'):
        with open(os.path.join(svg_dir, f), 'r', encoding='utf-8') as fp:
            content = fp.read()
        vb = re.search(r'viewBox="([^"]+)"', content)
        w = re.search(r'width="([^"]+)"', content)
        h = re.search(r'height="([^"]+)"', content)
        print(f"{f}: viewBox={vb.group(1) if vb else 'None'}, w={w.group(1) if w else 'None'}, h={h.group(1) if h else 'None'}")
