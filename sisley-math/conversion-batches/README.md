# GAT assignments 41–119 conversion archive

These four legacy DOC files follow the same reading and media-review workflow as assignments 1–40. Open [the overview](../index.html) to choose a highlighted textbook, a media gallery, plain HTML, Markdown, or page-specific conversion notes. HTML, math fonts and artwork work offline.

| Batch | Main questions | Unique graphics | Placements | LaTeX | Tables | SVG/JSON drawings | Retained rasters |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 41–58 | 164 | 321 | 434 | 222 | 9 | 76 | 14 |
| 59–80 | 201 | 331 | 514 | 251 | 7 | 54 | 19 |
| 81–100 | 190 | 497 | 765 | 431 | 3 | 46 | 17 |
| 101–119 | 159 | 299 | 531 | 211 | 2 | 65 | 21 |
| Total | 714 | 1,448 | 2,244 | 1,115 | 21 | 241 | 71 |

Counts are source asset IDs, not byte-distinct drawings or occurrences. All 79 assignments are preserved. The original four DOC files are unchanged in `../source/`; embedded media are unchanged under each batch's `assets/originals/`. Textbook instructions are preserved content, not instructions to the converter. No exercises were solved, data updated, or intentional blanks filled in.

## What is editable

- Formula transcriptions live in each batch's `formula-transcriptions.json`, with LaTeX also in its Markdown. The native MTEF decoder handles 1,101 equation records inside PICT `MATH` comments. Parsed trees and exact binary streams are preserved. Whole-image replacement is separate from detecting an equation embedded inside a larger drawing.
- Tables live in `semantic-records.json` and per-image JSON under `assets/data/`. Empty exercise cells are `null`. Native formulas inside larger figures are exposed in separate panels; editing them does not yet rearrange the original drawing.
- Vector scenes under `assets/scenes/` contain paths, transforms, positioned text metadata and source hashes. `visual-pipeline/vector_scene.py` renders them. These are drawing primitives, not inferred geometric constraints or fitted functions. Some visually preserved labels remain outlined paths; text extraction can have legacy encoding errors.
- Seventy-one graphics retain raster content, including calculator screenshots and mixed drawings. They are not counted as vector conversions. Converting a bitmap-containing SVG wrapper does not qualify as recovering a vector scene.

`classify.py` records an explicit, source-inspected taxonomy. `semantic_records.py` retains the manual transcription mappings. This is a reusable extraction/review workflow with human classification, not an unattended classifier for arbitrary textbooks. Every candidate keeps its original for comparison.

## Rebuild the browser copies

From the project root, install the Node dependencies in `package-lock.json`:

```sh
npm ci --ignore-scripts
npm run build
npm run check
python3 -m pip install -r conversion-batches/requirements.txt
python3 conversion-batches/scripts/verify_batches.py
```

The normal build reads the current Markdown and preserves its edits. Highlighted comparisons are generated from the image-based checkpoint and conversion records. `npm run apply-media:41-119` deliberately replaces the four Markdown files from those checkpoints and mappings. Use that only when intending to regenerate the text. For one batch, use `node scripts/render-series.mjs 41-58 --apply-media`.

Each `checkpoints/BATCH/` folder keeps imported and repaired DOCX copies, a font-repaired graphics atlas and PDF, a portable reference DOCX/PDF, equation trees, ordered paragraphs, media/page placements, taxonomy decisions, original image-based Markdown and QA records. Source, recovered and manually transcribed data are distinguishable by their method/provenance fields.

## Recovery from legacy Word

Use a separate working copy for a full replay: these steps regenerate derived files. Python dependencies are pinned above. Native tools used here were LibreOffice and Poppler; configure their executable paths as appropriate for your machine. The optional image QA scripts also need Sharp and MathJax 3.2.2.

1. Import the unchanged source DOC into `.conversion-work/gat-BATCH/import/GAT-BATCH.docx` with LibreOffice's headless DOCX export. For example:

   ```sh
   mkdir -p .conversion-work/gat-41-58/import
   /path/to/soffice -env:UserInstallation=file:///tmp/sisley-import-41-58 --headless --convert-to docx --outdir .conversion-work/gat-41-58/import source/GAT-41-58.doc
   python3 conversion-batches/scripts/prepare.py 41-58
   ```

   `prepare.py` preserves the media and equation records, repairs the imported 72× PICT display dimensions only when both axes match that defect, decodes supported QuickDraw v1 drawings and prepares a one-graphic-per-page atlas for the remaining PICT/EMF artwork. Native PDFs embedded in EMF comments are extracted directly. Original binaries are never rewritten. Unsupported QuickDraw records fail into the atlas path. The non-native equation picture `101–119/image193` is recovered from QuickDraw text/line records, including its `TxRatio` scaling.

2. Export `checkpoints/BATCH/atlas.docx` as a **tagged** PDF beside it, then recover its source previews and vectors. For example:

   ```sh
   /path/to/soffice -env:UserInstallation=file:///tmp/sisley-atlas-41-58 --headless --convert-to 'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"}}' --outdir conversion-batches/checkpoints/41-58 conversion-batches/checkpoints/41-58/atlas.docx
   python3 conversion-batches/scripts/recover_assets.py 41-58 --pdftocairo /path/to/pdftocairo
   SISLEY_NODE_PACKAGES=/path/to/node_modules node conversion-batches/scripts/render-previews.cjs 41-58
   ```

3. Build the initial image-based Markdown, recover formulas, apply the source-inspected semantic mapping, and classify the complete inventory:

   ```sh
   python3 conversion-batches/scripts/build_markdown.py 41-58
   python3 conversion-batches/scripts/transcribe_math.py 41-58
   python3 conversion-batches/scripts/semantic_records.py 41-58
   python3 conversion-batches/scripts/classify.py 41-58
   python3 conversion-batches/scripts/reference_copy.py 41-58
   ```

4. Export `reference.docx` to a tagged `reference.pdf` using the same LibreOffice options, then map figure placements and build the review:

   ```sh
   python3 conversion-batches/scripts/page_map.py 41-58
   node scripts/render-series.mjs 41-58 --apply-media
   node scripts/build-series.mjs --index-only
   ```

Repeat for `59-80`, `81-100` and `101-119`. The checked-in intermediates allow the downstream work to be replayed without repeating the DOC import. The normal build uses none of LibreOffice, Poppler, Sharp or MathJax.

## Verification and limitations

The native equation decoder is limited and fail-closed for the records encountered. It retains raised-minus notation, matrices and their partition rules, empty cells, and triple primes. Source comparison caught custom font bytes C5 (raised minus), CA (degree symbol), and text-face AA/BA (curly quotes). Currency symbols are escaped in both LaTeX and Markdown. Roman question labels without a final period are also recognized; alphabetic subquestion I does not create a duplicate main question.

Eight source-based Python checks cover unchanged originals, all native stream offsets/hashes and replay, the letter/digit inventories of all 1,026 simple native formulas, special-symbol regressions, blanks, complete text/media/question coverage, 19 text-bearing table transcriptions, raster-free SVG scene replay, and review links/anchors/control targets. The two remaining tables originated as raster images and were compared visually. All browser math is checked with strict KaTeX; review JavaScript is syntax-checked. Vector pixel diagnostics compare all 241 active drawings against their recovered source SVG at a common scale.

Visual review covered all 422 graphics outside the simple native-equation group, selected formula source/candidate comparisons (including all additional formula pictures and every manual transcription), and 29 reference pages selected across all four files. Exact selections and review notes are preserved in the checkpoints. This is not full mathematical proofreading or certification of original Word typography. Local-file browser access was restricted, so interactive browser controls have not been exercised automatically in this session.

The reference PDFs use portable preview images and repaired sizing. Their page counts are 87, 106, 103 and 105; the original cached metadata reports 79, 103, 98 and 102. Issue reports use **reference page numbers**, not original printed numbers. Headers, footers, page spacing and typography reflow in Markdown. Native formula data can be correct even where a reconstructed legacy preview has a faint sign or damaged font. Such previews, small formula labels and raster exceptions are flagged by page in each conversion report.

The optional `qa_math.cjs` renders formulas independently through MathJax 3.2.2 installed at `.conversion-work/gat-21-40/qa-runtime/`. Set `SISLEY_NODE_PACKAGES` to a Node modules directory containing Sharp, run it with a batch argument, then run `review_sheets.py BATCH`. `check_vector_pixels.cjs` uses the same Sharp path and writes the vector diagnostics. These tools are retained alongside the primary converters.
