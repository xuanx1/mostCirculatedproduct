"""
The EUR 500's security thread is embedded in the paper and does not show in a reflected-light scan,
so it is drawn here from the official descriptions:
  ECB: held against the light the thread appears as a dark stripe; the word "EURO" and the value
       ("500") can be seen in tiny letters on it.
  Deutsche Bundesbank: a dark line in the middle third of the note; "500 EURO" in small letters
       and "500" in microletters, alternating in normal and mirror writing.
Its position (x ~ 323 note units, read off the ECB Quick Guide's EUR 500 diagram) and its width
are approximate.

Writes assets/layers/front-thread.png, framed to THREAD_BOX (note units), and adds the box to
assets/boxes.js. Run: python tools/make_thread.py
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THREAD_BOX = (317, 0, 12, 320)                 # note units
PX_X, PX_Y = 3.2, 3.69                         # same scale as the other layers (0.75 x the artwork)
W, H = round(THREAD_BOX[2] * PX_X), round(THREAD_BOX[3] * PX_Y)
TW = round(4.2 * PX_X)                         # ~1 mm

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
x0 = (W - TW) // 2
d.rectangle([x0, 0, x0 + TW, H], fill=(58, 46, 70, 235))          # dark stripe against the light
d.line([x0, 0, x0, H], fill=(36, 28, 46, 255), width=1)
d.line([x0 + TW, 0, x0 + TW, H], fill=(36, 28, 46, 255), width=1)


def font(px):
    try:
        return ImageFont.truetype('arialbd.ttf', px)
    except OSError:
        return ImageFont.load_default()


# "500 EURO" in small letters and "500" in microletters, alternating normal and mirror writing
big, small = font(int(TW * 0.62)), font(int(TW * 0.36))
strip = Image.new('RGBA', (H, TW), (0, 0, 0, 0))
x, k = 8, 0
while x < H:
    word, f = ('500 EURO', big) if k % 2 == 0 else ('500', small)
    tw = int(ImageDraw.Draw(strip).textlength(word, font=f)) + 2
    tile = Image.new('RGBA', (tw, TW), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((1, TW * (0.14 if f is big else 0.3)), word, font=f, fill=(222, 214, 232, 255))
    if (k // 2) % 2 == 1:
        tile = ImageOps.mirror(tile)
    strip.alpha_composite(tile, (x, 0))
    x += tw + int(TW * 0.8)
    k += 1
img.alpha_composite(strip.rotate(90, expand=True), (x0, 0))
out = os.path.join(ROOT, 'assets', 'layers', 'front-thread.png')
img.save(out, optimize=True)
bpath = os.path.join(ROOT, 'assets', 'boxes.js')
txt = open(bpath, encoding='utf8').read()
boxes = json.loads(re.search(r'const BOXES = (\{.*\});', txt, re.S).group(1))
boxes['front-thread'] = list(THREAD_BOX)
open(bpath, 'w', encoding='utf8').write(txt.split('const BOXES')[0] + 'const BOXES = ' + json.dumps(boxes, indent=1) + ';\n')
print('thread ->', out, img.size)
