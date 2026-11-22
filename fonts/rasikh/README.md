# Rasikh (راسخ) — Arabic headline font, v0.2

A reconstruction of the Rawasekh headline lettering, requested by one of its
volunteer designers. **v0.2 traces the real letter shapes** out of published
post images with [VectorCraft](https://github.com/storytold/vectorcraft)'s Image
Trace (an open-source Illustrator alternative) instead of drawing them from
memory as v0.1 did. Name is a working title (`FAMILY` in `build.py`).

See `test/compare.png` (left: Rasikh, right: the original) and `test/specimen.png`.

## Status

- Regular weight only (Bold from v0.1 was dropped: it was the old geometric design).
- About 45 letter forms are traced directly from the source images. Forms that never
  appear in them are composed from traced parts: ط/ظ = ص's loop + ا's stem,
  final ع = ع's head + ج's bowl, final ن/ى/ي = س's flat bowl, final ق = ق's loop + that bowl,
  final م = the loop + a short tail.
- Composed forms that still need a designer's eye: isolated/final ق and ف, final ى/ن (small),
  final م's tail. Digits, harakat and Latin punctuation are still the v0.1 pen-drawn set.

## Files

| Path | What |
|---|---|
| `dist/Rasikh-Regular.{ttf,otf,woff2}` | The font (desktop, Canva / Figma, web) |
| `traced/*.png`, `traced/*.svg`, `traced/meta.json` | Each cut-out letter form, its VectorCraft trace, and where it was cut from |
| `trace.sh` | Runs VectorCraft Image Trace over `traced/*.png` |
| `assemble.py` | Builds the font from the traces (joins, dots, composed forms, OpenType features) |
| `build.py` | v0.1 pen-drawn glyphs; still supplies digits, harakat, punctuation and the feature code |
| `test/` | Specimen, letter-form grid, comparison page and renders |

## Rebuild

```bash
pip install fonttools brotli shapely svgelements
# VectorCraft CLI: cargo build --release -p vectorcraft-cli   (in a clone of storytold/vectorcraft)
VECTORCRAFT_CLI=/path/to/vectorcraft-cli fonts/rasikh/trace.sh   # only after changing traced/*.png
python3 fonts/rasikh/assemble.py                                # writes fonts/rasikh/dist/*
```

To improve a letter: replace its `traced/<name>.png` with a cleaner drawing (black on
white, same baseline position), run `trace.sh`, then `assemble.py`.

## Using it

- **Web:** `@font-face { font-family: Rasikh; src: url(Rasikh-Regular.woff2) format("woff2"); }`
- **Canva (Pro / Teams):** Brand Kit → Fonts → upload the `.ttf` / `.otf`.
- **Figma:** install the `.ttf` on the computer running Figma.
- **Kashida:** type the tatweel `ـ` to stretch words (e.g. `خســرناه`).

## License

Intended as a free waqf under the SIL Open Font License 1.1 (declared in the font).
Confirm with the Rawasekh team before public distribution.
