# Canadian $100 polymer note: security features

Interactive explorer of the Bank of Canada $100 polymer note, the first note of the Frontiers series
(issued 14 November 2011): Sir Robert L. Borden on the front, medical innovation on the back.
The images are the Bank of Canada's own specimen images.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Polymer · raised ink · large window · metallic portrait · metallic building · transparent text ·
small numbers · maple leaf border · frosted maple leaf window · hidden numbers; and the design elements
Sir Robert L. Borden (portrait), researcher at a microscope, insulin, DNA strand and ECG.

Feature wording follows the Bank of Canada ([$100 polymer note security features](https://www.bankofcanada.ca/banknotes/100-polymer-note-security-features/),
the employee handbook [*Canada's polymer notes*](https://www.bankofcanada.ca/wp-content/uploads/2012/05/employee_handbook.pdf),
pages 4 to 7, and the [*Check to Protect* poster](https://www.bankofcanada.ca/wp-content/uploads/2012/05/security_features_poster.pdf)).
Design elements follow [$100 polymer note design elements](https://www.bankofcanada.ca/banknotes/100-polymer-note-security-features/100-polymer-note-design-elements/)
and [*The Design of Canada's $100 Polymer Note*](https://www.bankofcanada.ca/wp-content/uploads/2013/05/design_100.pdf).

**Ultraviolet:** the Bank says polymer notes have *no* UV feature. The hidden numbers replaced the
UV check of the paper notes ([*Preparing for Canada's new polymer bank notes*](https://www.bankofcanada.ca/wp-content/uploads/2011/09/preparing_new_polymer_bank_notes.pdf), 2011).
So the UV view shows the note dark under the lamp with nothing glowing, and its overview says so.

## Controls

Same as the other pages: move to tilt, left-drag to rotate, right-drag to pan, wheel to zoom, drag an edge
to bend, and **G** fold · **E** explode · **F** flip · **R** reset · **Esc** back. Select *Hidden numbers*
and press *Look at a small light through it* to see the circle of 100s.

## How the polymer is shown

- **Windows:** the Bank's images keep the clear areas transparent (alpha). The page keeps them clear, so
  you see the page through the large window and the outline of the frosted leaf from either side, also
  when the note is bent or folded. A soft reflection slides over the clear window as the note tilts.
- **Metallic portrait and building:** holographic. They don't change face-on. As the note tilts, rainbow
  bands slide over them and they change colour. The building's colours step sharply, as the Bank
  describes. Both repeat on the back, as on the real note.
- **Transparent text:** the raised clear word *Canada* catches a glint as the note tilts.
- **Exploded view:** back print → metallic images → polymer film → metallic images → front print →
  clear raised text → raised ink. Both print layers keep their windows clear. The film layer is the
  single clear sheet with its windows.

## Illustrative, not exact

- **Hidden numbers:** the circle of 100s is drawn from the Bank's description ("a circle of numbers
  matching the value of the note"). No published image shows it, so its look and size are approximate.
- **Optical effects:** the colour changes, rainbow bands, glass reflection and glint are drawn to show
  the behaviour the Bank describes. They are not measured from a real note.
- **Polymer film layer:** the white base on the printed areas of the film is illustrative. The Bank
  says only that the note is "a single piece of polymer with some transparent areas".
- **Gold flow:** a highlight sweep through the portrait's and the researcher's line-work.
- **Artwork:** upscaled with Real-ESRGAN (`tools/upscale.py`). The upscaler sharpens line-work but
  cannot recover microprint the 1000 px source never had. These are the Bank's specimen images, so they
  carry its *SPECIMEN* overprint, which also lies across some cut-outs (portrait, researcher, ECG).

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `cad-100-front.png`, `cad-100-back.png` | working artwork, 2000 × 916 RGBA (the clear areas are transparent) |
| `assets/layers/` | feature cut-outs (each on its own box, `assets/boxes.js`) and the film layer |
| `assets/masks.css` | effect masks and line-work masks as data URIs, so the page works from `file://` |
| `assets/offset-*.webp` | print layers for the exploded view (windows clear, metallic images removed) |
| `assets/overrides/` | hand-cleaned cut-outs; these always win (none yet) |
| `feature-crops/` | every cut-out at full resolution, plus `contact-sheet.png` |
| `source/` | the Bank's original images and PDFs (`source/boc/`), the raw upscales, the SAM masks |
| `tools/upscale.py` | Real-ESRGAN x2 of colour and alpha, gentle levels |
| `tools/sam_isolate.py` | Segment Anything masks for the portrait, researcher, insulin bottle |
| `tools/cad_isolate.py` | all cut-outs, boxes, masks, print and film layers, contact sheet |

## Sources and credits

- **Base images:** Bank of Canada, [`100_front.png`](https://www.bankofcanada.ca/wp-content/uploads/2015/09/100_front.png)
  and [`100_back.png`](https://www.bankofcanada.ca/wp-content/uploads/2015/09/100_back.png) (1000 × 458, RGBA),
  as published on the $100 security-features page; the Bank of Canada Museum serves the same files. Source: Bank of Canada.
  **Wikimedia Commons has no usable image of this note.** Its [currency policy](https://commons.wikimedia.org/wiki/Commons:Currency)
  marks Canadian banknotes "Not OK", because the Bank of Canada holds the copyright. English Wikipedia
  has only 400 px non-free (fair-use) copies. Larger Bank photos (Flickr, 4096 px) show the note curled
  or at an angle, so they are not usable as flat artwork. They were used only as a reference for
  what the window looks like on a real note.
- **Facts:** issue date and theme from the Bank's [2011 press release](https://www.bankofcanada.ca/2011/11/bank-canada-issues-100-bill-first-canadian-polymer-bank-note/)
  and the [Bank of Canada Museum](https://www.bankofcanadamuseum.ca/complete-bank-note-series/2011-2013-polymer-series/polymer-series-100-note/)
  (size 152.4 × 69.85 mm; signature pairs, the specimen's being T. Macklem and M. Carney; "colour-shifting foil" in the window);
  design elements from the design-elements page and *design_100.pdf* above.
- **Title font:** Jost (SIL Open Font License 1.1, `fonts/OFL-Jost.txt`), a geometric sans close to the
  note's own rounded "Canada" and "100" lettering, bundled in `fonts/`. Body: Source Sans 3, Source Serif 4,
  IBM Plex Mono (OFL).
- **Palette:** the note's own browns, copper and cream.

## Reproduction rules (Canada)

From the Bank of Canada's [Using bank note images](https://www.bankofcanada.ca/banknotes/using-bank-note-images/):

- The Bank of Canada is the registered copyright owner of all design elements of Canadian bank notes.
  Criminal Code offences cover reproducing anything that looks like a current bank note.
- **Non-commercial use** (students, educators, bloggers) of the Bank's images needs no permission if the
  images are reproduced accurately and without alteration, credited "Source: Bank of Canada", and do not
  imply affiliation with or endorsement by the Bank.
- **Commercial use** needs the Bank's written permission. Colour reproductions must be one-sided.
  Physical copies must be no bigger than 114.3 × 52.39 mm or no smaller than 228.6 × 104.78 mm.
  "SPECIMEN" must be overprinted when more than half of one flat side is shown. Portraits must not be
  altered.
- **For this page:** it upscales, recolours and cuts the images apart, which goes beyond "without
  alteration". Check with the Bank (through its [reproduction request](https://www.bankofcanada.ca/banknotes/using-bank-note-images/submit-a-bank-note-image-reproduction-request/))
  before you publish it. The specimen images keep their SPECIMEN overprint. Printing or saving the page
  as a PDF covers the note with the EURion constellation.
