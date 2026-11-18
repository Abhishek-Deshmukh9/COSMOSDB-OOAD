import os
from PIL import Image

diag_dir = r'c:\Users\abhis\Desktop\Pjts\OOAD\diagrams'
pngs = sorted([f for f in os.listdir(diag_dir) if f.endswith('.png')])

for p in pngs:
    im = Image.open(os.path.join(diag_dir, p))
    w, h = im.size
    print(f"{p}: width={w}, height={h}, ratio={w/h:.2f}")
