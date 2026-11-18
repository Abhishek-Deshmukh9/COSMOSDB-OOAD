from PIL import Image
import os

diag_dir = r'c:\Users\abhis\Desktop\Pjts\OOAD\diagrams'

# Let's inspect unique features or sample pixel text boxes
# We can save small crops of each to inspect or print text lines if pytesseract is available
try:
    import pytesseract
    has_ocr = True
except ImportError:
    has_ocr = False

print('Has pytesseract:', has_ocr)

# Let's inspect the images by inspecting their color palette or text
for fname in sorted(os.listdir(diag_dir)):
    if fname.endswith('.png'):
        im = Image.open(os.path.join(diag_dir, fname))
        print(fname, im.size)
