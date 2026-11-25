# US $100 Federal Reserve note: security features

Interactive explorer of the current $100 design (in circulation since 8 October 2013). The note shown is Series 2021.

**Live:** [xuanx1.github.io/mostCirculatedproduct/usd-100](https://xuanx1.github.io/mostCirculatedproduct/usd-100/) · **Locally:** open `index.html` directly (works from `file://`).

## Features covered

3-D Security Ribbon · Bell in the Inkwell · colour-shifting 100 · portrait watermark · security thread (glows pink under UV) · raised printing · engraved portrait · microprinting · large gold 100 · serial numbers · Federal Reserve seal and bank indicator · Treasury seal · signatures · ultraviolet view.

Feature wording follows the U.S. Currency Education Program ([uscurrency.gov/denominations/100](https://www.uscurrency.gov/denominations/100)).

## Controls

Same as the S$10,000 page: move to tilt, left-drag to rotate, right-drag to pan, wheel to zoom, drag an edge to bend, and **G** fold · **E** explode · **F** flip · **R** reset · **Esc** back.

## Illustrative, not exact

- **3-D ribbon:** the bells and 100s on it are drawn over the ribbon, not the real micro-images.
- **Security thread:** a reflected-light image doesn't show it, so it is drawn from the official description, and its position is approximate.
- **Artwork:** upscaled with Real-ESRGAN and brightened (`tools/upscale.py`). The upscaler sharpens line-work but cannot recover microprint the source photo never captured.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `usd-100-front.png`, `usd-100-back.png` | working artwork (3072 × 1306) |
| `source/` | original images and raw upscales (not needed by the page) |
| `assets/`, `feature-crops/`, `tools/` | as in the S$10,000 folder; `tools/make_thread.py` draws the thread |

## Sources and credits

- **Back image:** [Wikimedia Commons, Reverse of the $100 Federal Reserve Note](https://commons.wikimedia.org/wiki/File:Reverse_of_the_$100_Federal_Reserve_Note.jpg), marked public domain.
- **Front image:** a Series 2021 photo supplied by the project owner (serial QC 02836101 A); confirm its rights before publishing.
- **Feature facts:** [uscurrency.gov](https://www.uscurrency.gov/denominations/100); circulation date from the Federal Reserve's 2013 announcement.
- **Title font:** Abril Fatface (SIL Open Font License), bundled in `fonts/`.
- **Reproduction rules:** [uscurrency.gov, Currency Image Use](https://www.uscurrency.gov/media/currency-image-use).
