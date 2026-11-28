"""
Latent images (潜像模様). Official: tilt the note and the front shows the face value 10000, the back
the letters NIPPON (BOJ security.htm; NPB design10).

Front: the 10000 is engraved into the cartouche at the bottom centre as areas of horizontal lines in a
ground of vertical lines (look closely at the artwork). The digits are found from the line direction
itself (oriented gradient energy), so the mask is the note's own latent 10000, not a drawn one:
  assets/layers/latent-front-mask.png   (box LATENT_FRONT in note units)
Back: NIPPON is engraved into the line pattern right of the watermark window. The photo resolves its
place (it shows faintly) but not crisp letter shapes, so the letters are the note's own NIPPON
wordmark (the top-left lettering, cut by isolate_features.py) fitted to that place. Illustrative:
  assets/layers/latent-back-mask.png    (box LATENT_BACK), and latent-back.png (its highlight)
Run after isolate_features.py:  python tools/latent.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
LATENT_FRONT = (300, 256, 118, 46)      # x, y, w, h note units: the cartouche's inner panel
LATENT_BACK = (443, 137, 113, 45)       # where NIPPON shows faintly on the back photo
PX = 3                                  # page layers: 3 px per note unit (1440 px face x 1.5)


def front():
    im = np.asarray(Image.open(os.path.join(ROOT, 'jpy-10000-front.png')).convert('L')).astype(np.float32)
    H, W = im.shape
    sx, sy = W / 720, H / 320
    x, y, w, h = LATENT_FRONT
    c = im[int(y * sy):int((y + h) * sy), int(x * sx):int((x + w) * sx)]
    gx = cv2.Sobel(c, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(c, cv2.CV_32F, 0, 1, ksize=3)
    ex = cv2.GaussianBlur(gx * gx, (0, 0), 5)
    ey = cv2.GaussianBlur(gy * gy, (0, 0), 5)
    r = ey / (ex + ey + 1e-3)                     # 1 = horizontal lines (the digits), 0 = vertical (the ground)
    m = ((r > 0.5) * 255).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
    # keep the five digits: the large pieces well inside the panel (the frame's own lines are horizontal too)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        X, Y, Wc, Hc, A = st[i]
        if A > 0.004 * m.size and Hc > 0.45 * m.shape[0] and Y > 2 and Y + Hc < m.shape[0] - 2:
            keep[lab == i] = 255
    a = cv2.GaussianBlur(keep.astype(np.float32) / 255, (0, 0), 1.2)
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((round(w * PX), round(h * PX)), Image.LANCZOS)
    rgba = Image.new('RGBA', out.size, (255, 255, 255, 0)); rgba.putalpha(out)
    rgba.save(os.path.join(LAYERS, 'latent-front-mask.png'), optimize=True)
    print('front latent: digits found', int((keep > 0).sum() > 0), 'pieces', n - 1)


def back():
    word = Image.open(os.path.join(LAYERS, 'back-wordmark.png')).convert('RGBA')
    a = np.asarray(word.getchannel('A'))
    ys, xs = np.nonzero(a > 40)
    word = word.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    x, y, w, h = LATENT_BACK
    al = word.getchannel('A').resize((round(w * PX), round(h * PX)), Image.LANCZOS)
    rgba = Image.new('RGBA', al.size, (255, 255, 255, 0)); rgba.putalpha(al)
    rgba.save(os.path.join(LAYERS, 'latent-back-mask.png'), optimize=True)
    # the highlight piece: the letters in the pattern's own rose-grey
    col = Image.new('RGBA', al.size, (150, 96, 104, 0)); col.putalpha(al.point(lambda v: int(v * 0.85)))
    col.save(os.path.join(LAYERS, 'latent-back.png'), optimize=True)
    print('back latent: wordmark', word.size, '->', al.size)


if __name__ == '__main__':
    front()
    back()
