"""
3D hologram (3Dホログラム): the stripe hologram's rotating portrait. Official: a stripe hologram whose
3D portrait turns as the note is tilted; a world first on a banknote (BOJ security.htm, NPB design10).

A photo holds only one angle, so the turning portrait comes from the Bank of Japan's own published
views of it (security.htm, image security6.png, saved in source/boj/): three views of the portrait
window at three angles. They are cut out (the white page and the foil's die-cut openings become
transparent) and registered onto the stripe: the BOJ draws the stripe at 1.247x in those views, and
the stripe's width and top match the note's stripe (x 70-115.5, from y 21 in note units).
Writes assets/layers/holo-a.png, holo-b.png, holo-c.png (box HOLO_FACE_BOX).
Run: python tools/hologram.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'boj', 'boj-security6-hologram.png')
VIEWS = {'a': (820, 251, 1058, 810), 'b': (1209, 252, 1446, 810), 'c': (1600, 255, 1838, 812)}   # px in the BOJ image
STRIPE_W = 45.5                     # note units (x 70 to 115.5)


def main():
    im = cv2.cvtColor(cv2.imread(SRC), cv2.COLOR_BGR2RGB).astype(np.float32)
    for k, (x0, y0, x1, y1) in VIEWS.items():
        c = im[y0:y1, x0:x1]
        # white (page, openings) -> transparent; a soft ramp keeps the lace edges smooth
        wht = c.min(2)
        a = np.clip((246 - wht) / 22, 0, 1)
        a = cv2.GaussianBlur(a, (0, 0), 0.6)
        # unmix the white from edge pixels so the cut-out has no white fringe
        safe = np.maximum(a, 0.05)[..., None]
        col = np.clip((c - 255 * (1 - safe)) / safe, 0, 255)
        w = round(STRIPE_W * 3)                                        # 3 px per note unit (page layers)
        h = round(w * c.shape[0] / c.shape[1])
        out = Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)
        out.save(os.path.join(ROOT, 'assets', 'layers', f'holo-{k}.png'), optimize=True)
    # the face box in note units: same width as the stripe; height from the views' own aspect
    hpx = STRIPE_W * 5 * (812 - 255) / (1838 - 1600)                  # artwork px (isotropic, 22.5 px/mm)
    print('HOLO_FACE_BOX = [70, 21, %.1f, %.1f]' % (STRIPE_W, hpx / (1710 / 320)))


if __name__ == '__main__':
    main()
