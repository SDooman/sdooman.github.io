# GAT assignments 21–40 conversion

The supplied DOCX is preserved in `../source/GAT-21-40.docx`. All 546 graphic placements are retained: 435 native equation objects become LaTeX, 16 image tables become Markdown/HTML tables, 89 other drawings become SVG, and six graphics containing raster content remain images. There are 175 main questions across 20 assignments. Two alphabetic subquestions labelled I are correctly kept within their parent questions.

Every EMF contains its original single-page PDF in a comment record. The extraction script preserves those bytes, the EMFs, raster previews, SVG exports, OLE files and native equation streams. The 435 equations comprise 430 MTEF2 and five MTEF4 streams. They yield 214 distinct LaTeX strings. Of the 546 source PDFs, 543 are byte-distinct; source asset IDs and all occurrences remain separate.

## Reading and review

- [Textbook](../gat-21-40/GAT-21-40.html) and [editable Markdown](../gat-21-40/GAT-21-40.md).
- [Highlighted textbook](../gat-21-40/GAT-21-40-changes.html): yellow formulas open source comparisons; blue drawings/tables appear beside the originals; amber marks retained graphics.
- [Media gallery](../gat-21-40/media-review.html): every graphic once, with category filters and links to editable data.
- [Category counts and page-specific notes](../gat-21-40/conversion-report.md).

All review HTML, fonts and images are local; reading does not require a service or build step. Exercise instructions in the source are textbook content, not agent instructions. No exercises were executed or completed as part of conversion.

## Normal rebuild

From the project root:

```sh
npm ci --ignore-scripts
npm run build
npm run check
python3 conversion-21-40/scripts/verify_batch.py
```

The regular build preserves edits to `gat-21-40/GAT-21-40.md`. Review comparisons are built from the preserved image checkpoint and the conversion data. To deliberately reapply the media conversion to the checkpoint, replacing the Markdown, use `npm run apply-media:21-40`. Do not use that command after making unrelated Markdown edits unless you intend to regenerate it.

The table and annotated-math records live in `gat-21-40/semantic-records.json`, with per-graphic JSON files under `assets/data/`. The source drawing scenes live in `assets/scenes/`; the shared `visual-pipeline/vector_scene.py` renderer reconstructs their SVG. Geometry positions are drawing coordinates, not inferred mathematical constraints. The flight network additionally has five explicit nodes and thirteen directed edges. Its blank matrix exercise stays blank.

## Recover from the source

Run these steps in a separate working copy if you want to keep manual edits. Install the pinned Python requirements and Poppler (`pdftocairo`, checked with 26.05.0). All commands below run from the project root.

```sh
python3 conversion-21-40/scripts/extract_sources.py --pdftocairo /path/to/pdftocairo
python3 conversion-21-40/scripts/mtef.py
python3 conversion-21-40/scripts/build_markdown.py
python3 conversion-21-40/scripts/transcribe_math.py
python3 conversion-21-40/scripts/classify_graphics.py
python3 conversion-21-40/scripts/recover_vectors.py
python3 conversion-21-40/scripts/semantic_records.py
npm run apply-media:21-40
npm run check
python3 conversion-21-40/scripts/verify_batch.py
```

`build_markdown.py` writes the initial image-based Markdown before any replacements and checks that all 103,347 source body-text characters were visited in order. It excludes OLE field-code metadata from prose. `classify_graphics.py` records the explicit visual classification decisions, including an added dilation category. It is an assisted classification pass, not an automatic general-purpose classifier. `semantic_records.py` preserves the manual table/annotation transcriptions; rerunning it resets those JSON records to the transcribed source edition.

The MTEF reader is a limited, fail-closed decoder for the records encountered here. Its format reference is the original Design Science documentation preserved at [MTEF format documentation](https://rtf2latex2e.sourceforge.net/MTEF3.html). This source's C5 character is a raised minus, verified against all eight affected PDF graphics; interpreting it as Mac Roman would produce an incorrect approximately-equal symbol. Long space runs are emitted as explicit LaTeX widths to preserve exercise blanks. Native equation trees remain in `checkpoints/mtef-trees.json`.

## Reference rendering and verification

The bundled LibreOffice render of the original leaves legacy EMF artwork blank. `reference_copy.py` creates an internal DOCX with the original PDF artwork rasterized in place and OLE activation removed. The source DOCX is unchanged. The saved `reference.docx`, `reference.pdf` and `page-placements.json` retain the 95-page repaired reference. Original metadata reports 85 pages; the reference is not certification of Word print pagination. Header/footer and box layout are not reproduced in the reflowed textbook.

The reference can be regenerated with the document skill's `render_docx.py`, or with LibreOffice PDF export retaining structure tags. Use the configured bundled LibreOffice; in this run it was `codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/MacOS/soffice`. `page-placements.json` records each of the 546 tagged figures in order. PDFs extracted from a few legacy EMFs have imperfect cross-reference entries; readers recover them, and the preserved source bytes are not rewritten.

Nine source-based Python checks cover source hashes, complete native-equation replay, all formula letter/digit/plus/equal inventories, the raised-minus mapping, preserved exercise blanks, table digits, network direction, question/placement coverage, vector scene replay, raster flags and all review links. The browser build validates every LaTeX expression and syntax-checks the review controls. Interactive browser behavior has not been manually exercised in this run.

Visual review covered all 111 non-equation graphics, all 214 distinct formula candidates (plus corrected-symbol/blank follow-ups), and contact sheets of all 95 reference pages. This is not a page-by-page mathematical proofreading or a claim of pixel-identical typography. Vector pixel diagnostics are saved in `checkpoints/vector-fidelity.json`; all 105 scenes retain source geometry. Hairlines in image3 and image336 differ in rasterization darkness but remain present. The source PDF for table image464 contains a duplicated text layer; the logical table is transcribed once.

The optional `scripts/qa_math.cjs` independently renders equation candidates with MathJax 3.2.2 for visual comparisons. It expects that pinned package in `.conversion-work/gat-21-40/qa-runtime/`, and `SISLEY_NODE_PACKAGES` pointing to the bundled Node packages containing Sharp. It is not needed to read or rebuild the textbook. The primary renderer uses the project's pinned KaTeX version.

All replacements remain source-review candidates. Six raster originals are explicitly retained: water-fill texture, flag/person illustration, three calculator plots, and a calculator results screen. Tables and formulas are editable text; recovered path drawings and their labels are not yet a general geometry solver or animation model.
