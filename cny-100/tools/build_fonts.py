"""
Builds fonts/ for the page: small woff2 subsets, all under the SIL Open Font License (licences in fonts/).

  python tools/build_fonts.py path/to/NotoSerifSC[wght].ttf path/to/MaShanZheng-Regular.ttf

  - 'CNY Title'  Noto Serif SC at weight 900: the title ¥100 and the strap. A Song (Ming) serif, the
                 style of the note's own 壹佰圆 lettering and of PBC's printed Chinese.
  - 'CNY Serif'  Noto Serif SC at weight 600: every Chinese character in the page's text.
  - 'CNY Cal'    Ma Shan Zheng, a brush script, for 中国人民银行 in the strap: the note's issuer name
                 is calligraphy.
  Each holds only the characters the page uses (collected from index.html, data.js and script.js),
  so the CJK fonts are a few tens of kB instead of 25 MB. Run it again after changing any Chinese text.
  Latin text uses Source Sans 3, Source Serif 4 and IBM Plex Mono (latin + latin-ext only), copied
  from ../usd-100/fonts/.
"""
import os, re, sys, shutil
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'fonts')
LATIN = ('latin', 'latin-ext')
KEEP = ('Source Sans 3', 'Source Serif 4', 'IBM Plex Mono')


def page_text():
    t = ''
    for f in ('index.html', 'data.js', 'script.js'):
        t += open(os.path.join(ROOT, f), encoding='utf8').read()
    return t


def cjk(text):
    return sorted({c for c in text if ord(c) > 0x2E7F})


def make(src, out, chars, wght=None):
    font = TTFont(src)
    if wght and 'fvar' in font:
        font = instancer.instantiateVariableFont(font, {'wght': wght})
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['*']
    opts.name_IDs = ['*']
    s = subset.Subsetter(opts)
    s.populate(text=''.join(chars))
    s.subset(font)
    font.flavor = 'woff2'
    font.save(os.path.join(FONTS, out))
    print(out, len(chars), 'glyphs', os.path.getsize(os.path.join(FONTS, out)), 'bytes')


def latin_css():
    """The latin + latin-ext @font-face rules of the text fonts, and their files, from the US $100 page."""
    src = os.path.join(ROOT, '..', 'usd-100', 'fonts')
    css = open(os.path.join(src, 'fonts.css'), encoding='utf8').read()
    out = []
    for sub, body in re.findall(r'/\* ([^*]+?) \*/\s*@font-face \{(.*?)\}', css, re.S):
        fam = re.search(r"font-family: '([^']+)'", body).group(1)
        if fam in KEEP and sub.strip() in LATIN:
            f = re.search(r'url\("\./([^"]+)"\)', body).group(1)
            shutil.copy(os.path.join(src, f), os.path.join(FONTS, f))
            out.append(f'/* {fam}, {sub.strip()} (SIL Open Font License) */\n@font-face {{{body}}}')
    return out


def main():
    noto, cal = sys.argv[1], sys.argv[2]
    os.makedirs(FONTS, exist_ok=True)
    for f in os.listdir(FONTS):
        os.remove(os.path.join(FONTS, f))
    text = page_text()
    chars = cjk(text)
    title = sorted(set('¥0123456789 ·') | set(c for c in chars))
    make(noto, 'cny-title.woff2', title, 900)
    make(noto, 'cny-serif.woff2', chars, 600)
    make(cal, 'cny-cal.woff2', sorted(set('中国人民银行')))
    rules = latin_css()
    rules += [
        "/* Noto Serif SC 900, subset to the page's characters (SIL Open Font License, fonts/OFL-NotoSerifSC.txt) */\n"
        "@font-face {\n  font-family: 'CNY Title';\n  font-weight: 900;\n  font-display: swap;\n  src: url(\"./cny-title.woff2\") format('woff2');\n}",
        "/* Noto Serif SC 600, subset to the page's Chinese characters (SIL Open Font License) */\n"
        "@font-face {\n  font-family: 'CNY Serif';\n  font-weight: 400 900;\n  font-display: swap;\n  src: url(\"./cny-serif.woff2\") format('woff2');\n  unicode-range: U+2E80-FFFF;\n}",
        "/* Ma Shan Zheng, subset to 中国人民银行 (SIL Open Font License, fonts/OFL-MaShanZheng.txt) */\n"
        "@font-face {\n  font-family: 'CNY Cal';\n  font-weight: 400;\n  font-display: swap;\n  src: url(\"./cny-cal.woff2\") format('woff2');\n}",
    ]
    open(os.path.join(FONTS, 'fonts.css'), 'w', encoding='utf8').write('\n'.join(rules) + '\n')
    here = os.path.dirname(noto)
    for lic in ('OFL-NotoSerifSC.txt', 'OFL-MaShanZheng.txt'):
        p = os.path.join(here, lic)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(FONTS, lic))
    print(len(chars), 'CJK characters:', ''.join(chars))


if __name__ == '__main__':
    main()
