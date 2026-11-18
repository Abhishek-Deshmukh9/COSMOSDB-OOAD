import os
from PIL import Image

diag_dir = r'c:\Users\abhis\Desktop\Pjts\OOAD\diagrams'
pngs = sorted([f for f in os.listdir(diag_dir) if f.endswith('.png')])

# Let's inspect the ODT sequence:
# [1] p: txt='Figure 1: ESI Search system' frames=[..., '349...'] -> Activity diagram Search System
# [3] p: txt='class diagram' frames=['CF5...'] -> Class diagram
# [4] p: txt='Esi Calc.' frames=['48D...'] -> Activity diagram ESI Calc
# [5] p: txt='Object diagram'
# [7] p: txt='Package Component' frames=['3F2...']
# [9] p: txt='.' frames=['502...']
# [11] p: txt='Sequence Compare Planets'
# [13] p: txt='.' frames=['406...']
# [15] p: txt='Sequence Search System'
# [17] p: txt='.' frames=['430...']
# [20] p: txt='State Planet Record'
# [21] p: txt='Figure 2: Use case diagram' frames=['21B...', '2C4...']

print('Checking crop info for PNGs...')
for p in pngs:
    im = Image.open(os.path.join(diag_dir, p))
    print(f'{p}: size={im.size}')
