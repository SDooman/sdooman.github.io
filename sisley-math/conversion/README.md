# Legacy document and image conversion

This folder preserves the actual recovery scripts used for `GAT 1-20.doc`, plus their intermediate inputs and the manually authored LaTeX transcription mapping. It is separate from the normal Markdown-to-HTML build in `../scripts/`.

`inventory.json` records the original and preserved script hashes, the few portability edits, and checkpoint hashes. Only machine-specific Node import paths and the Word source path were adjusted in the preserved scripts. The conversion algorithms and transcription choices are unchanged.

## Preserved scripts

| Script | Purpose |
| --- | --- |
| `inspect_document.py` | Reads the imported DOCX and corrects the image-size inflation that initially caused 1,351 pages. Produces `sized.docx`. |
| `pict_equations.py` | Decodes legacy PICT v1 drawing instructions, maps Symbol/MT Extra characters, and reconstructs equation SVGs, including radicals and matrix brackets. Produces 212 SVGs and `equations.json`. |
| `fix_pict2.py` | Adds explicit font-name resets to PICT v2 graphics so Symbol fonts do not leak into ordinary labels. Keeps original graphics unchanged. |
| `make_atlas.py` | Builds a DOCX with one non-equation graphic per page, applies corrected PICT files, and removes problematic EMF records for reliable rendering. |
| `render_equations.cjs` | Uses Sharp to render recovered SVGs to high-resolution PNGs for inspection. |
| `collect_images.py` | Crops diagram PNGs from rendered atlas pages using tagged PDF figure bounds; checks for blank images and builds contact sheets. |
| `build_markdown.py` | Extracts Word text, question IDs, image placements, page references, and initial conversion notes into Markdown and JSON. |
| `preview.cjs` | Historical image-stage HTML/Chrome preview and screenshot checks. It predates LaTeX; use the normal `npm run build` and `npm run check` for the current textbook. |
| `finalize.py` | Historical packaging step that added missing-worksheet notes and recorded the original manual/browser verification results. Those results are historical constants, not tests performed by this script. |
| `transcribe_formulas.py` | Applies the manually reviewed 220-image LaTeX mapping to the saved image-based Markdown. Records all 336 image decisions and replaces 546 placements. |

## Saved inputs

`checkpoints/` contains:

- The initial imported `GAT 1-20.docx` and size-corrected `sized.docx`.
- The 94-page tagged `sized.pdf`, which supplies reference pagination and placement bounds.
- `atlas.docx`, its tagged `atlas.pdf`, and diagram/equation extraction metadata.
- `pre-latex/`, the exact Markdown, manifest, report, README, and HTML immediately before the formula-transcription pass.

The original `.doc` remains in `../source/`; unchanged embedded PICT/EMF files remain in `../gat-1-20/assets/originals/`. The rendered atlas page PNGs can be regenerated from the saved atlas PDF and are not duplicated here.

## Replay in a separate working folder

The historical scripts write into `gat-1-20/` and `.conversion-work/` relative to the current directory. Use a separate directory so exploratory reruns cannot overwrite the checked-in, reviewed textbook.

Python dependencies are pinned in `requirements.txt`; Sharp, Playwright, and the historical Marked version are pinned in `package.json` and `package-lock.json`. The current HTML renderer has its own dependency files one directory above. The replay helper uses Python 3.9 or newer; use a Python version supported by the pinned packages.

From `sisley-math/`, prepare a new, nonexistent destination:

```sh
python3 conversion/prepare_replay.py /tmp/sisley-math-replay
cd /tmp/sisley-math-replay
python3 -m venv conversion/.venv
conversion/.venv/bin/python -m pip install -r conversion/requirements.txt
```

The helper verifies the inventory and copies the original graphics, current reading copy, renderer, and all required checkpoints into the new folder. It seeds `.conversion-work/pre-latex/` explicitly: the LaTeX script must start with image-based Markdown, not with already-transcribed Markdown.

Recover the equation SVGs and replay the reviewed LaTeX mapping:

```sh
conversion/.venv/bin/python conversion/scripts/pict_equations.py
conversion/.venv/bin/python conversion/scripts/transcribe_formulas.py
npm ci --ignore-scripts
npm run build
npm run check
```

Expected results: 212 recovered equation SVGs; 220 unique converted graphics in 546 LaTeX placements; 120 retained image placements; 170 question anchors. The generated Markdown and formula-transcription JSON can be compared byte for byte with the preserved reading copy. The replayed manifest retains historical verification fields from the image stage; rerun the checks rather than treating those fields as fresh validation.

## Other recovery stages

These commands also run from the isolated replay directory:

```sh
conversion/.venv/bin/python conversion/scripts/inspect_document.py
conversion/.venv/bin/python conversion/scripts/fix_pict2.py
conversion/.venv/bin/python conversion/scripts/make_atlas.py
```

The Word import, atlas PDF export, and PDF rasterization originally used LibreOffice and Poppler. They are external tools, not installed by the Python/Node dependency files. PDF export must retain document structure tags: the Python scripts use the PDF figure tags and bounding boxes to associate images with pages. Font availability and LibreOffice versions can change rendering and pagination; the saved DOCX/PDF checkpoints preserve the actual inputs used for this conversion.

For the saved atlas PDF, Poppler can recreate the expected 216-dpi page PNGs:

```sh
mkdir -p .conversion-work/atlas-pages
pdftoppm -r 216 -png .conversion-work/atlas.pdf .conversion-work/atlas-pages/page
npm ci --prefix conversion --ignore-scripts
node conversion/scripts/render_equations.cjs
conversion/.venv/bin/python conversion/scripts/collect_images.py
```

`collect_images.py` expects filenames such as `page-001.png` through `page-124.png`, letter-sized PDF pages, and three pixels per PDF point. Its equation PNGs are inspection outputs; copy them into `gat-1-20/assets/equations-png/` if updating the fallback set.

`build_markdown.py` can recreate the initial image-based text and manifest using the saved `sized.docx`, tagged `sized.pdf`, and metadata. It overwrites the text/report and predates subsequent editorial notes. The LaTeX pass deliberately reads the separately preserved `pre-latex/` checkpoint. `finalize.py` and `preview.cjs` are retained for provenance; they are not required for the current build and should not be used to claim new verification.

## Scope and limitations

This is document-specific recovery code, not a finished converter for arbitrary Word documents. In particular, `inspect_document.py` uses the original import's image-number threshold, the PICT parsers support the drawing instructions encountered in this source, and the LaTeX mapping was manually transcribed and reviewed. It is not OCR or a general image-to-LaTeX model. New textbooks will need their own extraction checks, mappings, page review, and missing-material notes.

## Verified replay

The preserved scripts were run in an isolated folder using these checkpoints. All 212 equation SVGs matched the preserved files byte for byte; the two regenerated DOCX archives had identical internal contents; the PICT v2 repair records matched; and all 124 extracted diagram PNGs matched the preserved pixels after rasterizing the saved atlas PDF. The image-stage Markdown and final LaTeX Markdown/transcription JSON also reproduced byte for byte. The normal HTML build and textbook checks passed after replay. A fresh Word-to-DOCX import and the historical Chrome preview were not rerun; those environment-sensitive steps remain documented rather than claimed as newly verified.
