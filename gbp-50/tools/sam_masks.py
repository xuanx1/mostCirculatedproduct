"""
Segment Anything (SAM, ViT-L) masks for the GBP 50 features that are distinct objects (foil patches,
windows, the portrait ovals, the Turing portrait, the ticker tape).

For each target SAM is prompted with the feature's box (plus positive points) on the upscaled artwork,
returns three candidate masks, and the best-scoring one that stays inside the box is kept. Only the mask
is stored (source/sam/<side>-<id>.png, full artwork resolution, white = feature); tools/cutouts.py turns
masks into clean alpha cut-outs of the original pixels, so nothing is redrawn.

Run (GPU, ~1 min):  python tools/sam_masks.py [id ...]
"""
import os, sys
import numpy as np
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'front': 'source/front-levelled.png', 'back': 'source/back-levelled.png'}
OUT = os.path.join(ROOT, 'source', 'sam')
VB_W, VB_H = 720, 320

# id -> (side, box x0,y0,x1,y1 in note units, positive points, negative points)
TARGETS = {
    'crown':        ('front', (124, 0, 202, 72), [(163, 38)], []),
    'hologram':     ('front', (124, 256, 202, 320), [(163, 289)], []),
    'small-window': ('front', (622, 246, 678, 318), [(650, 282)], []),
    'oval':         ('front', (34, 106, 124, 212), [(78, 160), (55, 140)], []),
    'frame':        ('front', (90, 76, 230, 248), [(105, 150), (212, 150), (160, 160)], []),
    'redfoil':      ('back', (524, 8, 590, 68), [(556, 38)], []),
    'small-window-b': ('back', (42, 246, 98, 318), [(70, 282)], []),
    'oval-b':       ('back', (596, 106, 688, 212), [(642, 160)], []),
    'frame-b':      ('back', (490, 76, 630, 248), [(508, 150), (615, 150), (560, 160)], []),
    'turing':       ('back', (298, 34, 484, 258), [(372, 130), (330, 60), (372, 235), (346, 208)], [(302, 100), (462, 150), (330, 266)]),
    'tape':         ('back', (16, 180, 246, 226), [(60, 197), (200, 214), (130, 207)], []),
}


def main(only):
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    os.makedirs(OUT, exist_ok=True)
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in SRC.items()}
    for fid, (side, bu, pos, neg) in TARGETS.items():
        if only and fid not in only:
            continue
        im = imgs[side]
        W, H = im.size
        sx, sy = W / VB_W, H / VB_H
        m = 10
        cx0, cy0 = max(0, bu[0] - m), max(0, bu[1] - m)
        cx1, cy1 = min(VB_W, bu[2] + m), min(VB_H, bu[3] + m)
        crop = im.crop((int(cx0 * sx), int(cy0 * sy), int(cx1 * sx), int(cy1 * sy)))
        P = lambda X, Y: [(X - cx0) * sx, (Y - cy0) * sy]
        box = P(bu[0], bu[1]) + P(bu[2], bu[3])
        pts = [P(*p) for p in pos] + [P(*p) for p in neg]
        labels = [1] * len(pos) + [0] * len(neg)
        inputs = proc(crop, input_boxes=[[box]], input_points=[[pts]], input_labels=[[labels]], return_tensors='pt').to(dev)
        with torch.no_grad():
            out = model(**inputs, multimask_output=True)
        masks = proc.image_processor.post_process_masks(out.pred_masks.cpu(), inputs['original_sizes'].cpu(),
                                                        inputs['reshaped_input_sizes'].cpu())[0][0].numpy()
        scores = out.iou_scores.cpu()[0, 0].numpy()
        bx0, by0, bx1, by1 = [int(v) for v in box]
        best, val = 0, -1
        for k in range(masks.shape[0]):
            inside = masks[k][by0:by1, bx0:bx1].sum() / max(1, masks[k].sum())
            v = scores[k] * inside
            if v > val:
                best, val = k, v
        full = np.zeros((H, W), np.uint8)
        x0, y0 = int(cx0 * sx), int(cy0 * sy)
        mk = masks[best].astype(np.uint8) * 255
        full[y0:y0 + mk.shape[0], x0:x0 + mk.shape[1]] = mk
        Image.fromarray(full).save(os.path.join(OUT, f'{side}-{fid}.png'), optimize=True)
        print(f'{side:5} {fid:15} mask {best} score {scores[best]:.3f} area {int((mk > 0).sum())}')


if __name__ == '__main__':
    main(set(sys.argv[1:]))
