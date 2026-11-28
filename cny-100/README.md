# ¥100 renminbi, 2015 edition (fifth series): security features

Interactive explorer of the current ¥100 note of the People's Bank of China (PBC): the 2015 edition of the fifth series, issued on 12 November 2015. Front: Mao Zedong. Back: the Great Hall of the People.

**Locally:** open `index.html` directly (works from `file://`).

> **Which edition.** There is no 2019-edition ¥100. PBC's 2019 edition of the fifth series covers only the ¥50, ¥20, ¥10 and ¥1 notes and the ¥1, 5 jiao and 1 jiao coins; the ¥100 in issue is the 2015 edition ([PBC, 中华人民共和国货币概况](https://www.pbc.gov.cn/huobijinyinju/147948/147954/147956/5204143/index.html); [PBC list of 2019-edition notes](https://www.pbc.gov.cn/huobijinyinju/147948/147954/148021/3871396/index.html)). The features asked for (the colour-shifting 100 with its moving bright bar, the colour-shifting windowed thread, the portrait and white watermarks, the see-through numeral) are the 2015 edition's.

## Features covered

Colour-shifting numeral 100 (光彩光变数字) · colour-shifting windowed thread (光变镂空开窗安全线) · portrait watermark (人像水印) · see-through numeral (胶印对印图案) · horizontal and vertical serial numbers (横竖双号码) · white watermark (白水印) · intaglio printing (雕刻凹印) · the engraved portrait · Braille mark (盲文面额标记) · microprinting (胶印缩微文字) · ultraviolet view (fluorescent fibres).

Wording and facts follow PBC (links below). The detail panel of the thread, both watermarks and the see-through numeral has **Hold up to the light**: the paper turns grey as it does against a lamp, the watermark darkens, the white 100 shows bright, the whole thread shows its "¥100" lettering and the reverse half of the numeral fills in the front half.

## Controls

Move to tilt (the colour shifts are driven by the viewing angle: none face-on), left-drag to rotate, right-drag to pan, wheel to zoom, drag an edge to bend, and **G** fold · **E** explode · **F** flip · **R** reset · **Esc** back. Labels fade their needles after 2 s; the note returns to rest after 10 s idle.

## Illustrative, not exact

- **Base images.** PBC's own specimen images (serial AA00000000) at 1599 × 795 px. They were resampled to 3100 × 1540 with Lanczos and a light unsharp mask. Real-ESRGAN x2 was run and rejected: on these images it turned the portrait's cross-hatching into invented vertical hatching and erased the microprinted "RMB100" lettering (its raw output is kept in `source/` for comparison). Nothing finer than PBC's image can be shown.
- **Specimen overprint removed.** PBC's images carry a teal 样币 overprint: large outlined 样 and 币 on each side (front: 样 in the watermark area, 币 over 壹佰圆; back: 样币 in the right panel) and a small 样币禁止流通 ("specimen, not for circulation") down the right edge of the front and along the bottom of the back. All of it was removed by LaMa inpainting (`tools/remove_specimen.py`, big-lama): only the characters' own pixels are masked (by the overprint's colour, inside a box per mark), the print around them fills the gap, and a few clean-up passes match the paper tone and the line patterns' colour. The serial AA00000000 is part of the printed design and is untouched. Under the strokes the print is reconstructed, not recovered: it is LaMa's continuation of the pattern around it, so at full zoom a faint softness can remain there (most visible under 币 on the front, where it crosses fine engraving). The untouched images are kept as `source/<side>-upscaled-specimen.png`.
- **Portrait watermark.** Rebuilt from the engraved portrait (its own silhouette, blurred to continuous tone). Position and size were measured, not guessed: PBC's transmitted-light animation of the watermark (`source/pbc/shuiyin.gif`) was registered to the front image, and the portrait fitted to the watermark face in it (scale 0.66, correlation 0.83). The rendering is an approximation of a mould-made watermark.
- **White watermark 100.** Place and size measured from PBC's animation of it (`source/pbc/baishuiyin.gif`, 240 × 200 px). The figures are clean geometry fitted to that image (each 0 an ellipse fitted to its bright ring, the 1 a stem and flag, one measured stroke width), drawn with smooth anti-aliased edges and open counters (`tools/make_watermarks.py`). The note's printed 100s are bold serif figures; the watermark in PBC's image is a light monoline 100, so its figures are not copied from the print. Stroke weight and the exact figure shapes are approximate.
- **Whole thread.** A reflected-light image shows only the thread's five windows (cut from the artwork). The full thread with its "¥100" lettering (seen against the light, and in the exploded view) is drawn from PBC's description (`tools/make_thread.py`); the lettering's size and spacing are illustrative.
- **Colour shifts.** Gold to green and the rolling bright bar (numeral), magenta to green (thread) are hue cross-fades and a masked band driven by the tilt angle, a model of what PBC describes, not a measurement of the inks.
- **Not drawn: the magnetic thread.** PBC says a second, fully embedded magnetic thread lies on the other side of the note from the windowed one, but does not publish its position, so it is mentioned and not drawn.
- **Ultraviolet.** PBC's 2015 ¥100 pages do not describe the note's fluorescent print. The only UV fact used is PBC's statement that the fifth-series paper contains colourless fluorescent fibres (无色荧光纤维); the fibres' number, positions and colour are illustrative. Nothing else is lit.
- **Microprinting.** Listed by PBC for the 1999 and 2005 editions ("RMB" and "RMB100" in the oval pattern at the top of the front); the same pattern and lettering can be seen on PBC's 2015 specimen image.
- **Offset layers** in the exploded view are the artwork with the line-work suppressed (`tools/isolate_features.py`), an approximation of the underprint.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `cny-100-front.png`, `cny-100-back.png` | working artwork (3100 × 1540, the note's 155 × 77 mm) |
| `source/pbc/` | PBC originals: `front-l.jpg`, `back-l.jpg` and the transmitted-light / tilt animations used for registration |
| `source/*-esrgan-x2.png` | the rejected Real-ESRGAN upscale, for comparison (not used by the page) |
| `source/*-upscaled-specimen.png` | the working artwork before the overprint was removed (input of `remove_specimen.py`) |
| `assets/layers/` | the cut-outs (glow highlights, exploded view); `assets/masks.css` the effect masks as data URIs; `assets/boxes.js` their boxes |
| `assets/overrides/` | hand-cleaned cut-outs here always win (none yet) |
| `feature-crops/` | full-resolution cut-outs and a contact sheet |
| `fonts/` | woff2 subsets (see below) |
| `tools/upscale.py` | crop the PBC frame, resample, level |
| `tools/remove_specimen.py` | removes PBC's 样币 overprint by LaMa inpainting (reads `source/<side>-upscaled-specimen.png`, writes the working artwork; `--preview` writes the mask overlay) |
| `tools/extract_features.py` → `tools/isolate_features.py` | colour-separated cut-outs, masks, offset layers, boxes; then `tools/clean_assets.js` deletes unused layers |
| `tools/sam_isolate.py` | Segment Anything cut-outs: portrait, National Emblem (GPU) |
| `tools/make_watermarks.py`, `tools/make_thread.py` | portrait and white watermarks, see-through fit; the whole thread |
| `tools/build_fonts.py` | builds `fonts/` from Noto Serif SC and Ma Shan Zheng |

Rebuild order: `upscale.py` → `remove_specimen.py` (after a new upscale, delete `source/*-upscaled-specimen.png` first so it is taken from the new images) → `extract_features.py` → `sam_isolate.py` → `make_watermarks.py` → `make_thread.py` → `isolate_features.py` (refreshes masks and runs the clean-up) → `build_fonts.py` after any change to Chinese text.

## Sources and credits

- **Images.** Wikimedia Commons has no usable image: Commons treats renminbi designs as copyrighted ("Not OK", [Commons:Copyright rules by territory/China, Currency](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/China#Currency)). The page therefore uses the People's Bank of China's own published specimen images of the 2015 ¥100, from PBC's feature page: [front-l.jpg](https://www.pbc.gov.cn/rmyh/xbrmb/imgs/front-l.jpg) and [back-l.jpg](https://www.pbc.gov.cn/rmyh/xbrmb/imgs/back-l.jpg), 1599 × 795 px each, © People's Bank of China; and PBC's animations `shuiyin.gif`, `baishuiyin.gif`, `anquanxian.gif`, `duiyinzheng.gif`, `guangbian1.gif` from the same folder (used to locate the watermarks and check the thread and numeral behaviour). See the reproduction rules below before publishing.
- **Feature facts:**
  - PBC, 2015 ¥100 feature page: [Chinese](https://www.pbc.gov.cn/rmyh/xbrmb/index.html), [English](https://www.pbc.gov.cn/rmyh/xbrmb/index_english.html) (issue date, every feature's description).
  - PBC, [2015年版第五套人民币100元纸币](https://www.pbc.gov.cn/huobijinyinju/147948/147954/148021/3871273/3871275/index.html) (unchanged, added, adjusted and removed features).
  - PBC, [答记者问 on the issue of the 2015 ¥100](https://www.pbc.gov.cn/huobijinyinju/147948/147954/147956/8a1e3c51c8b44cfebb59feae8177a21f/index.html) (4 mm thread, the second magnetic thread, why two serial numbers, the clearer watermark).
  - PBC, [第五套人民币100元纸币防伪特征 (1999)](https://www.pbc.gov.cn/huobijinyinju/147948/147954/148021/176741/2025080619260380847/index.html) (size 155 × 77 mm, microprinting) and [2005年版 100元](https://www.pbc.gov.cn/huobijinyinju/147948/147954/148021/176764/2820779/index.html) (microprinting kept).
  - PBC, [中华人民共和国货币概况 (January 2024)](https://www.pbc.gov.cn/huobijinyinju/147948/147954/147956/5204143/index.html) (issue dates of the 2015 and 2019 editions; colourless fluorescent fibres in the fifth-series paper).
- **Title fonts** (SIL Open Font License, licence texts in `fonts/`): Noto Serif SC, a Song serif like the note's 壹佰圆 and PBC's printed Chinese, for ¥100 and the Chinese strap; Ma Shan Zheng, a brush script, for 中国人民银行 (the note's issuer name is calligraphy). Both are subset to the page's ~70 characters (`tools/build_fonts.py`, about 38 kB together). Text: Source Sans 3, Source Serif 4, IBM Plex Mono (SIL OFL), latin subsets from the US $100 page.
- **Theme:** the note's red (PBC red, #b3121f) on white paper, with the gold of the colour-shifting 100 running through the title.

## Reproduction rules for renminbi

The use of renminbi images is governed by PBC's *Measures for the Administration of the Use of Renminbi Designs* (人民币图样使用管理办法, PBC Order [2019] No. 2, in force 15 November 2019): [PBC announcement](https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2025092212550177557/index.html), [full text in the State Council Gazette](https://www.gov.cn/gongbao/content/2020/content_5471439.htm). In short:

- Using a complete or partial renminbi design in publicity material, publications or other goods needs approval from the local PBC branch (Art. 5–8), except that publishers, teaching and research bodies, news media and museums in China may use designs from the **PBC website's design library** for teaching, research, public education or public-interest publicity without approval, still subject to Art. 9 (Art. 15).
- Art. 9: use one side only; do not harm the image of renminbi or let the public mistake it for money; keep the portrait and National Emblem in proportion, undistorted; mark the design with a clearly legible 图样 ("design") in the middle, at least a third of its length and width, unless (among other exceptions) one side is under 50 % of actual size, or on a digital carrier the resolution is below 28 px/cm (72 dpi); goods may not carry the bank's name or the currency unit.
- Penalties apply to unapproved or non-compliant use (Art. 16–17).

This page shows both sides at high resolution, so it does not meet Art. 9 as it stands. Its images are PBC's own specimen images with PBC's 样币 overprint removed (by LaMa inpainting, `tools/remove_specimen.py`), and they carry no 图样 marking either: the Measures require such a marking on reproductions (Art. 9) unless an exception applies, so removing PBC's mark moves the page further from compliance, not closer. Treat it as a private study: **the owner must check the Measures, and obtain PBC approval if required, before publishing it.** The print/PDF export covers the note with the EURion constellation, as on the other pages.
