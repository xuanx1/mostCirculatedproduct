"""
Build the page's title and Chinese fonts as small local woff2 files (both SIL Open Font License).

  python tools/subset_fonts.py Inter[opsz,wght].ttf NotoSansTC[wght].ttf

Sources (Google Fonts repository):
  https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf
  https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf

Inter (the title: the note's numerals and the bank's name are a clean grotesque sans) is cut to
Latin; Noto Sans TC (a Hei face like the bank's Chinese name on the note) is cut to exactly the
Chinese characters the page uses, read from index.html, data.js and script.js. Re-run after changing any
Chinese text. Appends the @font-face rules to fonts/fonts.css (replacing earlier ones).
"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'fonts')
MARK = '/* --- title and Chinese faces (tools/subset_fonts.py) --- */'


def cut(src, dst, text=None, unicodes=None):
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['*']
    opts.name_IDs = ['*']
    font = TTFont(src)
    s = subset.Subsetter(opts)
    s.populate(text=text or '', unicodes=unicodes or [])
    s.subset(font)
    font.flavor = 'woff2'
    font.save(dst)
    return os.path.getsize(dst)


def main():
    inter, noto = sys.argv[1], sys.argv[2]
    page = ''.join(open(os.path.join(ROOT, f), encoding='utf-8').read() for f in ('index.html', 'data.js', 'script.js'))
    han = sorted(set(re.findall(r'[　-〿㐀-鿿＀-￯]', page)))
    latin = list(range(0x20, 0x7f)) + list(range(0xa0, 0x100)) + [0x2013, 0x2014, 0x2018, 0x2019, 0x201c, 0x201d, 0x2026, 0x00b7]
    n1 = cut(inter, os.path.join(FONTS, 'inter-latin.woff2'), unicodes=latin)
    n2 = cut(noto, os.path.join(FONTS, 'noto-sans-tc-subset.woff2'), text=''.join(han) + '·')
    print('inter', n1, 'bytes; noto sans tc', n2, 'bytes,', len(han), 'characters:', ''.join(han))
    css = open(os.path.join(FONTS, 'fonts.css'), encoding='utf-8').read().split(MARK)[0].rstrip() + '\n\n' + MARK + """
/* Inter (SIL Open Font License): the title amount. Variable weight, Latin only. */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("./inter-latin.woff2") format('woff2');
}
/* Noto Sans TC (SIL Open Font License): cut to the Chinese characters this page uses. */
@font-face {
  font-family: 'Noto Sans TC';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("./noto-sans-tc-subset.woff2") format('woff2');
}
"""
    open(os.path.join(FONTS, 'fonts.css'), 'w', encoding='utf-8').write(css)


if __name__ == '__main__':
    main()
