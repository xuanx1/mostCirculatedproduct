"""
Segment Anything (SAM ViT-L) masks for the $100 Frontier note's distinct objects, on the working artwork.

For each target SAM is prompted with the object's box (plus positive points), returns three candidate
masks, and the best-scoring one that stays inside the box is kept (largest parts, holes filled).
Only the mask is written (source/sam/<side>-<id>.png, full size); tools/cad_isolate.py applies it to the
original pixels and frames the layer.

  python tools/sam_isolate.py          (facebook/sam-vit-large, cached after the first run)
"""
import os
import numpy as np
import cv2
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'source', 'sam')
VB_W, VB_H = 720, 320

# id -> (side, box x0,y0,x1,y1 in note units, positive points, negative points)
TARGETS = {
    'portrait':   ('front', (214, 6, 452, 320), [(330, 110), (300, 270), (400, 280)], [(170, 200)]),
    'researcher': ('back', (282, 12, 484, 262), [(320, 120), (400, 110), (300, 60)], [(260, 230)]),
    'insulin':    ('back', (428, 184, 480, 280), [(452, 245), (452, 200)], []),
    'dna':        ('back', (452, 28, 612, 178), [(500, 70), (560, 120)], [(620, 230)]),
}


def load_model():
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    return (SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval(),
            SamProcessor.from_pretrained('facebook/sam-vit-large'), dev)


def main():
    model, proc, dev = load_model()
    os.makedirs(OUT, exist_ok=True)
    for fid, (side, bu, pos, neg) in TARGETS.items():
        im = Image.open(os.path.join(ROOT, f'cad-100-{side}.png')).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
        img = bg.convert('RGB')
        W, H = img.size
        sx, sy = W / VB_W, H / VB_H
        m = 12
        cx0, cy0 = max(0, bu[0] - m), max(0, bu[1] - m)
        cx1, cy1 = min(VB_W, bu[2] + m), min(VB_H, bu[3] + m)
        cb = (int(cx0 * sx), int(cy0 * sy), int(cx1 * sx), int(cy1 * sy))
        crop = img.crop(cb)
        P = lambda X, Y: [(X - cx0) * sx, (Y - cy0) * sy]
        box = P(bu[0], bu[1]) + P(bu[2], bu[3])
        pts = [P(*q) for q in pos + neg]
        lbl = [1] * len(pos) + [0] * len(neg)
        inp = proc(crop, input_boxes=[[box]], input_points=[[pts]], input_labels=[[lbl]], return_tensors='pt').to(dev)
        with torch.no_grad():
            out = model(**inp, multimask_output=True)
        masks = proc.image_processor.post_process_masks(out.pred_masks.cpu(), inp['original_sizes'].cpu(),
                                                        inp['reshaped_input_sizes'].cpu())[0][0].numpy()
        scores = out.iou_scores.cpu()[0, 0].numpy()
        bx0, by0, bx1, by1 = [int(v) for v in box]
        best = max(range(len(masks)), key=lambda k: scores[k] * masks[k][by0:by1, bx0:bx1].sum() / max(1, masks[k].sum()))
        mk = (masks[best] > 0).astype(np.uint8) * 255
        n, lab, st, _ = cv2.connectedComponentsWithStats(mk, 8)
        if n > 1:
            big = st[1:, cv2.CC_STAT_AREA].max()
            mk = np.isin(lab, [k for k in range(1, n) if st[k, cv2.CC_STAT_AREA] >= big * 0.02]).astype(np.uint8) * 255
        ff = np.pad(mk, 1).copy(); cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (0, 0), 255)
        mk |= cv2.bitwise_not(ff)[1:-1, 1:-1]
        full = np.zeros((H, W), np.uint8); full[cb[1]:cb[3], cb[0]:cb[2]] = mk
        Image.fromarray(full).save(os.path.join(OUT, f'{side}-{fid}.png'), optimize=True)
        print(f'{side:5} {fid:12} mask {best} score {scores[best]:.3f}')


if __name__ == '__main__':
    main()
