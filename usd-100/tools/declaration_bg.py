"""
Page background: the Declaration of Independence itself, from the Library of Congress's scan of the
1823 William Stone facsimile (public domain; Wikimedia Commons
File:US_Declaration_of_Independence_us0036_03.jpg, saved in source/found/). The heading and the opening
lines, which hold the passage printed on the $100, are separated from the parchment (ink darker than
the local background) and written as brown ink on transparency: assets/declaration-bg.png.
Run: python tools/declaration_bg.py
"""
import os
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'found', 'declaration_stone1823_loc_us0036_03.jpg')
AREA = (255, 340, 7310, 2720)          # px: heading and the first lines
INK = (74, 52, 30)
OUT_W = 2600

im = Image.open(SRC).convert('L').crop(AREA)
im = im.resize((OUT_W, round(im.height * OUT_W / im.width)), Image.LANCZOS)
L = np.asarray(im).astype(np.float32)
bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))), (0, 0), 6)
ink = bg - L
a = np.clip((ink - 14) / 45, 0, 1)
out = np.dstack([np.full_like(L, INK[0]), np.full_like(L, INK[1]), np.full_like(L, INK[2]), a * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(os.path.join(ROOT, 'assets', 'declaration-bg.png'), optimize=True)
print('declaration-bg', out.shape[1], 'x', out.shape[0])
