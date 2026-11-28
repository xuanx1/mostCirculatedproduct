"""
Title / Japanese font: Shippori Mincho B1 (SIL Open Font License 1.1, The Shippori Mincho Project
Authors, github.com/fontdasu/ShipporiMincho; via Google Fonts). The full fonts are ~15 MB each, so
each weight is subset to exactly the characters the page uses (ASCII, ¥, and every Japanese character
in index.html, data.js and script.js) and written as WOFF2 in fonts/, with its @font-face rules in
fonts/shippori.css. Re-run after changing any Japanese text on the page.

  python tools/subset_fonts.py path/to/folder-with-ShipporiMinchoB1-*.ttf
(needs fontTools and brotli: pip install fonttools brotli)
"""
import os, sys
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS = {400: 'Regular', 700: 'Bold', 800: 'ExtraBold'}


def page_chars():
    text = ''.join(open(os.path.join(ROOT, f), encoding='utf8').read() for f in ('index.html', 'data.js', 'script.js'))
    chars = {c for c in text if ord(c) > 0x7e}
    chars |= {chr(c) for c in range(0x20, 0x7f)}
    return ''.join(sorted(chars))


def main():
    src = sys.argv[1]
    chars = page_chars()
    css = ['/* Shippori Mincho B1 (SIL OFL 1.1), subset to the characters this page uses: tools/subset_fonts.py */']
    for w, name in WEIGHTS.items():
        out = os.path.join(ROOT, 'fonts', f'shippori-mincho-b1-{w}.woff2')
        opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['*']; opts.name_IDs = ['*']
        f = subset.load_font(os.path.join(src, f'ShipporiMinchoB1-{name}.ttf'), opts)
        sub = subset.Subsetter(opts); sub.populate(text=chars); sub.subset(f)
        subset.save_font(f, out, opts)
        css.append("@font-face{font-family:'Shippori Mincho B1';font-style:normal;font-weight:%d;font-display:swap;"
                   "src:url(shippori-mincho-b1-%d.woff2) format('woff2')}" % (w, w))
        print(os.path.basename(out), os.path.getsize(out), 'bytes')
    open(os.path.join(ROOT, 'fonts', 'shippori.css'), 'w', encoding='utf8').write('\n'.join(css) + '\n')
    print(len(chars), 'characters')


if __name__ == '__main__':
    main()
