"""
Tiles for the 3-D Security Ribbon, taken from the note itself instead of drawn icons:
  bell: the Liberty Bell (with its yoke) from the Bell in the Inkwell, cut out of the uscurrency.gov
        Decoding Dollars scan (source/found/...declaration-seal-bell...4558w.jpg) with Segment Anything;
  100:  the silhouette of the note's own 100 (the colour-shifting 100, counters open).
Both are written as pale, ribbon-coloured PNGs to assets/layers/ribbon-bell.png / ribbon-100.png.
Run: python tools/ribbon_tiles.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'found', 'usd100_front_partial_declaration-seal-bell_uscurrency-decoding-pdf_4558w.jpg')
INKWELL = (2613, 1234, 471, 456)          # px in that scan
FILL = (22, 30, 104)            # dark blue: the ribbon's images read darker than the band


def bell():
    """SAM (ViT-L) on the inkwell, prompted on the bell and its yoke, negative on the inkwell around it."""
    import sys, torch
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sam_isolate as SI
    im = Image.open(SRC).convert('RGB')
    x, y, w, h = INKWELL
    crop = im.crop((x, y, x + w, y + h))
    model, proc, dev = SI.load_model()
    pos = [(235, 90), (160, 120), (310, 120), (235, 260), (180, 330), (300, 330), (240, 370)]
    neg = [(60, 200), (420, 200), (235, 30), (60, 420), (420, 420), (100, 80)]
    inputs = proc(crop, input_boxes=[[[105, 50, 375, 400]]], input_points=[[pos + neg]],
                  input_labels=[[[1] * len(pos) + [0] * len(neg)]], return_tensors='pt').to(dev)
    with torch.no_grad():
        out = model(**inputs, multimask_output=True)
    masks = proc.image_processor.post_process_masks(out.pred_masks.cpu(), inputs['original_sizes'].cpu(),
                                                    inputs['reshaped_input_sizes'].cpu())[0][0].numpy()
    scores = out.iou_scores.cpu()[0, 0].numpy()
    def val(k):
        mk = masks[k]
        return scores[k] * np.mean([mk[q[1], q[0]] for q in pos]) * (1 - np.mean([mk[q[1], q[0]] for q in neg]))
    k = max(range(masks.shape[0]), key=val)
    print('bell mask', k, [round(float(val(i)), 3) for i in range(masks.shape[0])])
    a = SI.clean(masks[k], 0.05)
    g = np.asarray(crop).astype(np.float32).mean(-1); sel = a > .5
    tex = 0.86 + 0.14 * np.clip((g - g[sel].mean()) / (g[sel].std() + 1e-3), -2, 2) / 2   # keep some engraving
    rgbo = np.clip(np.array(FILL)[None, None] * tex[..., None], 0, 255)
    out = Image.fromarray(np.dstack([rgbo, a * 255]).astype(np.uint8), 'RGBA')
    Image.fromarray(np.dstack([np.asarray(crop), (a * 255).astype(np.uint8)]), 'RGBA')         .crop(out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())         .save(os.path.join(ROOT, 'feature-crops', 'front', 'ribbon-bell-source.png'), optimize=True)
    out = out.crop(out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    out.thumbnail((140, 140), Image.LANCZOS)
    out.save(os.path.join(ROOT, 'assets', 'layers', 'ribbon-bell.png'), optimize=True)
    return out.size


def hundred():
    c = Image.open(os.path.join(ROOT, 'assets', 'layers', 'front-ovi-100-cut.png')).getchannel('A')
    c = c.crop(c.point(lambda v: 255 if v > 8 else 0).getbbox())
    out = Image.new('RGBA', c.size, FILL + (0,)); out.putalpha(c)
    out.thumbnail((150, 150), Image.LANCZOS)
    out.save(os.path.join(ROOT, 'assets', 'layers', 'ribbon-100.png'), optimize=True)
    return out.size


TILE = (116, 140)          # the ribbon's 58 x 70 px tile, at 2x


def pad(name, fit):
    """Centre the cut-out on a transparent tile the ribbon repeats, scaled to fit (w, h) inside it."""
    p = os.path.join(ROOT, 'assets', 'layers', name)
    im = Image.open(p).convert('RGBA'); im.thumbnail(fit, Image.LANCZOS)
    t = Image.new('RGBA', TILE, FILL + (0,))
    t.alpha_composite(im, ((TILE[0] - im.width) // 2, (TILE[1] - im.height) // 2))
    t.save(p, optimize=True)


if __name__ == '__main__':
    import sys
    if '--100' not in sys.argv:
        print('bell', bell()); pad('ribbon-bell.png', (78, 96))
    print('100', hundred()); pad('ribbon-100.png', (92, 40))
