# Most Circulated Product: banknote security features

Interactive, educational explorers of the security features on the highest-denomination banknote of each of the ten most traded currencies (by the BIS Triennial Central Bank Survey of foreign exchange turnover). Tilt, flip, bend, fold, explode into layers and view under ultraviolet light, with every feature labelled and explained.

Landing page: [xuanx1.github.io/mostCirculatedproduct](https://xuanx1.github.io/mostCirculatedproduct/)

| Currency | Note | Live page | Folder | Status |
|---|---|---|---|---|
| US dollar | $100 Federal Reserve note (Series 2021) | [usd-100](https://xuanx1.github.io/mostCirculatedproduct/usd-100/) | [`usd-100/`](usd-100/) | Live |
| Euro | €500 (Europa series) ¹ | | `eur-500/` | Planned |
| Japanese yen | ¥10,000 (2024 series) | | `jpy-10000/` | Planned |
| Pound sterling | £50 (Bank of England, polymer) | | `gbp-50/` | Planned |
| Chinese renminbi | ¥100 (2019 edition) | | `cny-100/` | Planned |
| Swiss franc | CHF 1000 (ninth series) | | `chf-1000/` | Planned |
| Australian dollar | $100 (polymer, next generation) | | `aud-100/` | Planned |
| Canadian dollar | $100 (polymer, Frontier series) | | `cad-100/` | Planned |
| Hong Kong dollar | HK$1,000 (2018 series) ² | | `hkd-1000/` | Planned |
| Singapore dollar | S$10,000 (Portrait Series) ¹ | [sgd-10000](https://xuanx1.github.io/mostCirculatedproduct/sgd-10000/) | [`sgd-10000/`](sgd-10000/) | Live |

¹ Still legal tender but no longer issued: the €500 since 2019, the S$10,000 since 2014. They remain the highest denominations of their currencies.
² Hong Kong notes are issued by three banks (HSBC, Standard Chartered, Bank of China), each with its own design.

## Every explorer has

- **Pointer tilt and drag-rotate.** Optical features (colour-shifting ink, foil, 3-D ribbon, latent image, watermark) respond to the real viewing angle, not a timer.
- **Bend and fold** (drag an edge, **G**), **flip** (**F**), **explode** into print and paper layers (**E**), and an **ultraviolet** view.
- **Labels with needles** around the flat note, and detail callouts when you zoom into a feature.
- **Printing or saving as PDF** prints a flat front covered by the EURion constellation, the ring pattern many colour copiers detect.
- **Plain files.** Every page opens directly from disk (`file://`) as well as on GitHub Pages; all fonts and images are local.

## Folder layout

Each note lives in its own folder (`<currency>-<denomination>/`) with its page (`index.html`, `script.js`, `styles.css`, `data.js`), its artwork, the isolated features (`feature-crops/`), page layers (`assets/`) and the tools that extract them (`tools/`). See each folder's README for sources and credits.

## Reproductions

These pages are for education about anti-counterfeiting features. The note images are reproductions for illustration only and are not legal tender. Each issuer sets its own rules for reproducing its notes. Check them before publishing:

- **US dollar:** colour images are restricted by law (18 U.S.C. § 504; 31 CFR § 411): one-sided, and below 75% or above 150% of actual size. The US page shows both sides interactively, which does not fit those conditions as written.
- **Singapore dollar:** the Currency Act and MAS guidelines.
- **Other currencies:** the rules of the ECB, Bank of Japan, Bank of England, People's Bank of China, Swiss National Bank, Reserve Bank of Australia, Bank of Canada and Hong Kong Monetary Authority (and the three Hong Kong note-issuing banks).
