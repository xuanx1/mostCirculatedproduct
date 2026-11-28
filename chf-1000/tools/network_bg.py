"""
Page background: the note's own 'open network' illustration, as the SNB printed it in its brochure
"The new 1000-franc note" (page 6, source/found/snb-brochure-open-network.png). The white paper is
keyed out, so only the purple lines remain, and the page shows them very faintly.

  python tools/network_bg.py
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
im = Image.open(os.path.join(ROOT, 'source', 'found', 'snb-brochure-open-network.png')).convert('RGB')
im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
a = np.asarray(im, np.float32)
lum = a @ np.array([.299, .587, .114], np.float32)
alpha = np.clip((250 - lum) / 120, 0, 1)
col = np.empty(a.shape, np.float32)
col[...] = (92, 64, 160)                      # the note's purple
out = Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8), 'RGBA')
out.save(os.path.join(ROOT, 'assets', 'network-bg.png'), optimize=True)
print(out.size)
