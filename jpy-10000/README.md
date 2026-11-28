# ¥10,000 Bank of Japan note (2024): security features

Interactive explorer of the ¥10,000 Bank of Japan note issued from **3 July 2024**: Shibusawa Eiichi (渋沢栄一) on the front, the Marunouchi building of Tokyo Station on the back. The National Printing Bureau prints it.

**Locally:** open `index.html` directly (it works from `file://`).

## Features covered

3D hologram (the stripe hologram's portrait turns as you tilt) · high-definition watermark (the portrait in the blank oval) · bar-pattern watermark (three bars) · latent images (10000 on the front, NIPPON on the back) · pearl ink (pink sheen at both ends) · microprinting (NIPPONGINKO) · deep intaglio printing · identification marks (eleven raised diagonal lines) · luminescent ink and the ultraviolet view · the intaglio portrait and vignette · larger numerals.

Every fact comes from the Bank of Japan and the National Printing Bureau:

- BOJ, *新しい日本銀行券の特徴* (features of the new notes): [boj.or.jp/note_tfjgs/note/n_note/security.htm](https://www.boj.or.jp/note_tfjgs/note/n_note/security.htm)
- BOJ, *新しい日本銀行券* (the issue date, 3 July 2024): [boj.or.jp/note_tfjgs/note/n_note/index.htm](https://www.boj.or.jp/note_tfjgs/note/n_note/index.htm)
- NPB, *F一万円券* (the design, the 160 × 76 mm size, and the feature wording): [npb.go.jp/ja/n_banknote/design10/](https://www.npb.go.jp/ja/n_banknote/design10/)

## Controls

These match the other explorers: move the pointer to tilt, left-drag to rotate, right-drag to pan, wheel to zoom, drag an edge to bend. Keys: **G** fold · **E** explode · **F** flip · **R** reset · **Esc** back. The watermark and bar-pattern cards have a **Hold up to the light** button.

## Illustrative, not exact

- **Hologram:** a photo captures one angle only. The turning portrait uses the BOJ's three published views of it (`security6.png`), cross-faded by the side-to-side tilt. The rainbow bands are drawn. Face-on you see the photo's own hologram.
- **Watermarks:** a photo taken in reflected light doesn't show them, so they are rebuilt (`tools/watermark.py`):
  - The portrait comes from the note's own engraved portrait, softened to continuous tone and placed in the blank oval.
  - The watermark shows the portrait only, rebuilt from the engraved portrait and fitted to the oval's ring. The fine pattern the BOJ describes around it is not drawn, because no image shows it closely enough. The three bars are drawn from the BOJ's diagrams; their bar widths are approximate. The bars' position, right of the portrait, was read from the BOJ's picture.
- **Latent images:** the front 10000 is the note's own: its digits are found from the direction of the engraved lines (`tools/latent.py`). The photo shows where NIPPON sits on the back but not its letter shapes, so the NIPPON is the note's own NIPPON lettering fitted to that place.
- **Pearl ink:** a clear coat that is invisible in a photo. The two end bands follow the BOJ diagram, and their exact extent is approximate.
- **Ultraviolet:** the glow map is traced from the BOJ's own UV photo of the front (`security11.png`, `tools/uv_map.py`). That photo is low resolution, so the glow's fine texture comes from the daylight artwork's pink tint. The NPB says parts of the back glow too, but no official image shows which, so the back shows no glow.
- **Microprinting:** the photo doesn't resolve the letters. The two marked places follow the BOJ's diagram.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `jpy-10000-front.png`, `jpy-10000-back.png` | working artwork: 3600 × 1710, the note's 160 : 76 |
| `source/` | the original Commons photos, and in `source/boj/` the two BOJ images used (hologram views, UV photo); the page doesn't need them |
| `assets/` | page layers (`layers/`), effect masks as data URIs (`masks.css`), offset-print layers, `boxes.js`; hand-cleaned files go in `overrides/` |
| `feature-crops/` | each isolated feature at full resolution |
| `fonts/` | Source Serif 4 / Source Sans 3 / IBM Plex Mono (latin), and Shippori Mincho B1 subset to the page's characters |
| `tools/` | `prepare_art.py` flattens and levels the photos. `extract_features.py` runs the whole build: box crops, then `build.py` (`isolate_features`, `circle_cut`, `sam_isolate`, `engrave_cut`, `watermark`, `latent`, `hologram`, `pearl`, `uv_map`, masks). `subset_fonts.py` subsets the font. `clean_assets.js` drops unused layers. |

How the cut-outs were made:

- **Seal:** an exact circle, found from the seal's own vermilion.
- **Portrait and lower-right 10000 plate:** Segment Anything (ViT-L).
- **Tokyo Station and the cartouche:** cut along their own engraving.
- **10000 numerals, identification marks, NIPPON:** colour or darkness separation, with the counters left open.

## Sources and credits

- **Front image:** [Wikimedia Commons, *Series F 10K Yen Bank of Japan note - obverse.jpg*](https://commons.wikimedia.org/wiki/File:Series_F_10K_Yen_Bank_of_Japan_note_-_obverse.jpg), by Heavy Frisker, **CC BY-SA 4.0**. The original is 3696 × 1808 px. It was flattened, cropped to the note edge and levelled (`tools/prepare_art.py`). It was large enough that no AI upscaling was used.
- **Back image:** [Wikimedia Commons, *Series F 10K Yen Bank of Japan note - reverse.jpg*](https://commons.wikimedia.org/wiki/File:Series_F_10K_Yen_Bank_of_Japan_note_-_reverse.jpg), by Heavy Frisker, **CC BY-SA 4.0**. The original is 3592 × 1736 px, processed the same way.
- Because of CC BY-SA, the working artwork and the layers cut from it are adaptations shared under **CC BY-SA 4.0**, with the same attribution.
- **Hologram views and UV photo:** from the Bank of Japan's page above (`security6.png`, `security11.png`). The BOJ says it does not provide high-resolution note images; questions about using its images go to the BOJ (see below).
- **Title and Japanese font:** [Shippori Mincho B1](https://github.com/fontdasu/ShipporiMincho), by The Shippori Mincho Project Authors, **SIL Open Font License 1.1** (`fonts/OFL-ShipporiMincho.txt`). It is a Mincho, like the engraved kanji on the note (壱万円 · 日本銀行券). Each weight is subset to about 30 KB.
- **Other fonts:** Source Serif 4, Source Sans 3 and IBM Plex Mono, all **SIL OFL 1.1**.
- **Palette:** taken from the note: washi cream, the plum-brown of the portrait, and the vermilion (朱) of the Governor's seal and the back's large 10000.

## Reproduction rules (Japan)

- The **Act on Control of Imitation of Currency and Securities** (通貨及証券模造取締法, 1895), Article 1, prohibits making or selling anything whose appearance could be confused with a Bank of Japan note. Article 2 sets the penalty. The BOJ lists these laws at [boj.or.jp/note_tfjgs/note/security/gizo0410a.htm](https://www.boj.or.jp/note_tfjgs/note/security/gizo0410a.htm).
- The Ministry of Finance [FAQ](https://www.mof.go.jp/faq/currency/07af.htm) explains how this applies:
  - Using a note's design, in part or in whole, on goods or printed matter may breach the Act.
  - It is judged as a whole: how closely the design is imitated, the size, the material, and whether the words 「見本」 (specimen) or diagonal lines are present.
  - Posting photos on a website is not itself covered, but printing such images may breach the Act.
  - The Ministry cannot rule in advance on whether a particular use is allowed.
- The BOJ asks that questions about using the note images it publishes be sent to it at the address on the page above.
- These pages are for education about anti-counterfeiting features, and the images are not legal tender. **Printing or saving the page as PDF** gives a flat front covered by the EURion constellation pattern. That pattern deters copying; it is not proof that a print is lawful.
