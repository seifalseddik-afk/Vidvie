# Rasikh (راسخ) — Arabic headline font, v0.1 draft

A working reconstruction of the Rawasekh headline typeface, built from published
post images at the request of one of its volunteer designers. Name is a working
title and can be changed in `build.py` (`FAMILY`).

**Status: first draft.** Shaping works end to end (all letters in isolated /
initial / medial / final forms, lam-alef ligatures, harakat positioning, digits,
punctuation). The letterforms are a geometric approximation and still differ
from the original — see `test/compare.png`. Letter-by-letter review by the
designers is the next step.

## Files

| Path | What |
|---|---|
| `dist/Rasikh-{Regular,Bold}.ttf` | Install on desktop, upload to Canva / Figma |
| `dist/Rasikh-{Regular,Bold}.otf` | Same, CFF outlines (print / Adobe apps) |
| `dist/Rasikh-{Regular,Bold}.woff2` | Web (`@font-face`) |
| `build.py` | Source of every glyph (skeleton + pen) and the OpenType features |
| `test/` | Specimen, letter-form grid and comparison pages + renders |

## Rebuild

```bash
pip install fonttools brotli shapely
python3 fonts/rasikh/build.py        # writes fonts/rasikh/dist/*
node fonts/rasikh/test/shot.js "$PWD/fonts/rasikh/test/specimen.html" out.png   # needs playwright
```

## How the font is made

Each glyph is a set of centre-line paths (`P(x, y).L(...).Q(...).C(...)`) stroked
with an elliptical pen, then merged into clean outlines. Pen size = weight
(`WEIGHTS`), so editing one skeleton updates Regular and Bold together.
`WX` stretches all Arabic letters horizontally; `A`, `T`, `H`, `BOT` set the
alef height, tooth height, head height and bowl depth.

## Using it

- **Web:** `@font-face { font-family: Rasikh; src: url(Rasikh-Regular.woff2) format("woff2"); }`
- **Canva (Pro / Teams):** Brand Kit → Fonts → upload the `.ttf` / `.otf`.
- **Figma:** install the `.ttf` on the computer running Figma (desktop app or font installer).
- **Kashida:** type the tatweel `ـ` to stretch words (e.g. `خســرناه`).

Latin letters are not included yet; browsers fall back to another font for them.

## License

Intended to be released as a free waqf under the SIL Open Font License 1.1
(declared in the font's name table). Confirm with the Rawasekh team before
public distribution.
