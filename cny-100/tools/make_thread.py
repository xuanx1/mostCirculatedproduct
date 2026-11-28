"""
The ¥100's colour-shifting windowed thread, whole, as it lies in the paper (illustrative).

PBC: the thread is 4 mm wide, on the right of the obverse; it shows magenta face-on and green at an
angle, and against the light the demetallised characters "¥100" can be read in it, alternately
the right way round and mirrored (正反交替排列的镂空文字 "¥100").
(pbc.gov.cn/huobijinyinju/147948/147954/148021/3871273/3871275/index.html and the PBC Q&A.)

A reflected-light image shows only its five windows (cut from the artwork by isolate_features.py);
this draws the full length for the exploded view and for "seen against the light". The lettering's
size, spacing and font are illustrative.

Writes assets/layers/thread-full.png, framed to the box [592.5, 0, 20, 320] note units (data.js).
Run: python tools/make_thread.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (592.5, 0, 20, 320)
PXU_X, PXU_Y = 1440 / 720 * 1.5, 715 / 320 * 1.5
W, H = round(BOX[2] * PXU_X), round(BOX[3] * PXU_Y)
TW = round(18.6 * PXU_X)                  # 4 mm of the note's 155 mm = 18.6 note units

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
x0 = (W - TW) // 2
# the metal: dark violet-grey, as the windows read against the light
metal = Image.new('RGBA', (TW, H), (58, 44, 66, 240))
# demetallised "¥100", along the thread, alternately right way round and mirrored
try:
    font = ImageFont.truetype('arialbd.ttf', int(TW * 0.62))
except OSError:
    font = ImageFont.load_default()
strip = Image.new('L', (H, TW), 0)
ds = ImageDraw.Draw(strip)
x, k = 8, 0
while x < H:
    word = '¥100'
    w = int(ds.textlength(word, font=font))
    tile = Image.new('L', (w + 2, TW), 0)
    ImageDraw.Draw(tile).text((1, TW * 0.14), word, font=font, fill=255)
    if k % 2:
        tile = ImageOps.mirror(tile)
    strip.paste(tile, (x, 0))
    x += w + int(TW * 0.8)
    k += 1
letters = strip.rotate(90, expand=True)           # reading up the thread
a = metal.getchannel('A').point(lambda v: v)
a.paste(0, mask=letters)                            # the letters are clear film: no metal
metal.putalpha(a)
img.alpha_composite(metal, (x0, 0))
out = os.path.join(ROOT, 'assets', 'layers', 'thread-full.png')
img.save(out, optimize=True)
print('thread ->', out, img.size)
