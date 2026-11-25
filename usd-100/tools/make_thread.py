"""
The $100's security thread is embedded in the paper and does not show in a reflected-light scan,
so it is drawn here from the official description: a thread running vertically to the left of the
portrait, imprinted with USA and 100 in an alternating pattern (uscurrency.gov/denominations/100).
Its exact position on this artwork is approximate.

Writes assets/layers/front-thread.png, framed to the box [152, 0, 15, 320] note units (data.js).
Run: python tools/make_thread.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX_W, BOX_H = 15, 320                        # note units
PX_PER_UNIT_X, PX_PER_UNIT_Y = 1440 / 720 * 1.5, 612 / 320 * 1.5   # same scale as the other page layers
W, H = round(BOX_W * PX_PER_UNIT_X), round(BOX_H * PX_PER_UNIT_Y)
THREAD_W = round(5 * PX_PER_UNIT_X)           # ~1 mm on the real note

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
x0 = (W - THREAD_W) // 2
d.rectangle([x0, 0, x0 + THREAD_W, H], fill=(214, 206, 196, 235))     # the plastic thread, seen in transmitted light
d.line([x0, 0, x0, H], fill=(160, 150, 140, 255), width=1)
d.line([x0 + THREAD_W, 0, x0 + THREAD_W, H], fill=(160, 150, 140, 255), width=1)

# USA and 100, alternating, reading up the thread
try:
    font = ImageFont.truetype('arialbd.ttf', int(THREAD_W * 0.62))
except OSError:
    font = ImageFont.load_default()
strip = Image.new('RGBA', (H, THREAD_W), (0, 0, 0, 0))
ds = ImageDraw.Draw(strip)
x, words, k = 6, ['USA', '100'], 0
while x < H:
    w = ds.textlength(words[k % 2], font=font)
    ds.text((x, THREAD_W * 0.12), words[k % 2], font=font, fill=(70, 60, 52, 255))
    x += w + THREAD_W * 0.9
    k += 1
img.alpha_composite(strip.rotate(90, expand=True), (x0, 0))
out = os.path.join(ROOT, 'assets', 'layers', 'front-thread.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, optimize=True)
print('thread ->', out, img.size)
