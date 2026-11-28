"""
Security-feature effects for the landing page's hover preview, built from each explorer's own
feature cut-outs (assets/layers/<side>-<id>.png, placed by assets/boxes.js in note units).

For every note, the features that react to tilting are listed in FX with how they react:
  ovi    colour-shifting ink: the feature's own shape takes a shifted colour as the note tilts
  holo   hologram / foil / metallic: a rainbow band sweeps across the feature's own shape
  wm     watermark: fades in as the note tilts toward the light
Each shape is written as a small data-URI mask (so masks load from file:// too) into fx.js, with its box
as a fraction of the note. The upright CHF 1000 is turned a quarter turn, like its thumbnail.

Run from the project root:  python tools/make_fx.py
"""
import base64, io, json, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# folder: (note space w, h, rotate a quarter turn for the landscape thumbnail)
SPACE = {'usd-100': (720, 320, 0), 'eur-500': (720, 320, 0), 'jpy-10000': (720, 320, 0), 'gbp-50': (720, 320, 0),
         'cny-100': (720, 320, 0), 'chf-1000': (320, 722, 1), 'aud-100': (720, 320, 0), 'cad-100': (720, 320, 0),
         'hkd-1000': (720, 320, 0), 'sgd-10000': (720, 320, 0)}
# (layer key, kind); 'f' / 'b' side comes from the key's prefix
FX = {
    'usd-100':   [('front-ovi-100', 'ovi'), ('front-bell', 'ovi'), ('front-ribbon', 'holo')],
    'eur-500':   [('front-hologram', 'holo'), ('back-ovi', 'ovi')],
    'jpy-10000': [('front-hologram', 'holo')],
    'gbp-50':    [('front-hologram', 'holo'), ('front-crown', 'holo'), ('front-windowfoil', 'holo'),
                  ('back-redfoil', 'holo'), ('back-windowfoil', 'holo')],
    'cny-100':   [('front-ovmi', 'ovi'), ('front-thread', 'holo')],
    'chf-1000':  [('front-globe', 'ovi'), ('front-strip', 'holo')],
    'aud-100':   [('front-fan3d', 'holo'), ('front-colourowl', 'holo'), ('front-rolling', 'ovi'), ('back-rolling', 'ovi')],
    'cad-100':   [('front-mportrait', 'holo'), ('front-mbuilding', 'holo'), ('back-mportrait', 'holo'), ('back-mbuilding', 'holo')],
    'hkd-1000':  [('front-shimmer', 'holo'), ('front-thread', 'holo'), ('front-mane', 'holo')],
    'sgd-10000': [('front-kinegram', 'holo'), ('front-ovi-10000', 'ovi')],
}
# watermarks: the explorers' rebuilt watermark-ghost layer, where its box is set in their script (boxes.js wins)
WM = {'usd-100': [613, 66, 80, 110], 'eur-500': [6, 58, 160, 186], 'jpy-10000': [313, 62, 158, 171],
      'cny-100': [24.28, 75.28, 134.64, 145.2], 'chf-1000': [62, 526, 216, 132], 'hkd-1000': [502.65, 126.34, 168.78, 102.47],
      'sgd-10000': [23, 106, 148, 168]}
MAX_PX = 360          # longest side of each mask (the preview is ~440 px wide)


def boxes(folder):
    s = open(os.path.join(ROOT, folder, 'assets', 'boxes.js'), encoding='utf8').read()
    return json.loads(re.search(r'=\s*(\{[\s\S]*\})', s).group(1))


def layer(folder, key):
    for name in (f'{key}.png', f'{key}-cut.png'):
        p = os.path.join(ROOT, folder, 'assets', 'layers', name)
        if os.path.exists(p):
            return p
    return None


def data_uri(im, keep_colour):
    buf = io.BytesIO()
    if keep_colour:
        im.save(buf, 'WEBP', quality=62)
        return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    a = im.getchannel('A')
    m = Image.new('LA', im.size, 255); m.putalpha(a)
    m.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    out, total = {}, 0
    for folder, items in FX.items():
        W, H, rot = SPACE[folder]
        bx = boxes(folder)
        rows = []
        for key, kind in items:
            p = layer(folder, key)
            if key not in bx or not p:
                print(f'  skip {folder} {key}: {"no box" if key not in bx else "no layer"}'); continue
            x, y, w, h = bx[key]
            im = Image.open(p).convert('RGBA')
            if rot:   # quarter turn anticlockwise, as PIL's rotate(90) used for the thumbnail
                im = im.rotate(90, expand=True)
                x, y, w, h = y, W - x - w, h, w
                fw, fh = H, W
            else:
                fw, fh = W, H
            im.thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)
            uri = data_uri(im, kind == 'wm')
            total += len(uri)
            rows.append({'side': 'b' if key.startswith('back') else 'f', 'kind': kind,
                         'box': [round(x / fw, 5), round(y / fh, 5), round(w / fw, 5), round(h / fh, 5)], 'src': uri})
        wm_box = bx.get('watermark-ghost', WM.get(folder))
        p = layer(folder, 'watermark-ghost')
        if wm_box and p:
            for side in ('f', 'b'):                       # in the paper: seen mirrored from the back
                x, y, w, h = wm_box
                im = Image.open(p).convert('RGBA')
                if side == 'b':
                    im = im.transpose(Image.FLIP_LEFT_RIGHT); x = W - x - w
                if rot:
                    im = im.rotate(90, expand=True); x, y, w, h = y, W - x - w, h, w; fw, fh = H, W
                else:
                    fw, fh = W, H
                im.thumbnail((200, 200), Image.LANCZOS)         # watermarks are soft: small is enough
                uri = data_uri(im, True); total += len(uri)
                rows.append({'side': side, 'kind': 'wm', 'src': uri,
                             'box': [round(x / fw, 5), round(y / fh, 5), round(w / fw, 5), round(h / fh, 5)]})
        out[folder] = rows
        print(folder, len(rows), 'effects')
    js = ('// generated by tools/make_fx.py: tilt effects for the hover preview, from each explorer\'s own cut-outs\n'
          'window.NOTE_FX = ' + json.dumps(out, separators=(',', ':')) + ';\n')
    open(os.path.join(ROOT, 'fx.js'), 'w', encoding='utf8').write(js)
    print(f'fx.js {len(js) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
