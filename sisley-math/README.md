# Sisley math textbook preservation

This folder preserves GAT assignments 1–119 from the supplied high-school math textbook, including the original Word documents, editable Markdown and LaTeX, recovered graphics, offline browser reading copies, and conversion records.

## Assignments 41–119

[Open the review overview](index.html) to choose a highlighted textbook or media gallery. The four new batches preserve 79 assignments, 714 main question anchors and 2,244 graphic placements. Counts below are **unique graphics**, so an image reused in several exercises counts once.

| Assignments | LaTeX formulas | Editable tables | SVG/JSON drawings | Retained raster graphics |
| --- | ---: | ---: | ---: | ---: |
| [41–58](gat-41-58/GAT-41-58-changes.html) | 222 | 9 | 76 | 14 |
| [59–80](gat-59-80/GAT-59-80-changes.html) | 251 | 7 | 54 | 19 |
| [81–100](gat-81-100/GAT-81-100-changes.html) | 431 | 3 | 46 | 17 |
| [101–119](gat-101-119/GAT-101-119-changes.html) | 211 | 2 | 65 | 21 |
| Total | 1,115 | 21 | 241 | 71 |

Each batch includes Markdown, offline HTML, an original-versus-candidate media gallery, category counts and page-specific issues. Yellow formulas open source comparisons; blue drawings and tables show both versions; amber marks retained artwork. These remain review candidates. Native equations found within composite drawings are exposed separately, but do not yet relayout those drawings.

The [Python/JavaScript scripts and replay instructions](conversion-batches/README.md), source documents, original embedded media, native equation records, reference copies and conversion checkpoints are preserved. The native equation reader recovered 1,101 records from legacy PICT comments. The new batch checks also verify all 1,026 simple native formulas against the source letter/digit inventories, 19 text-bearing table transcriptions and the 241 active vector drawings. See the conversion documentation for the scope and limits of visual QA.

## Assignments 21–40

- [Read assignments 21–40](gat-21-40/GAT-21-40.html) or [edit the Markdown](gat-21-40/GAT-21-40.md).
- [Review highlighted changes in context](gat-21-40/GAT-21-40-changes.html) or [skim all media comparisons](gat-21-40/media-review.html).
- [See category counts and page-specific issues](gat-21-40/conversion-report.md).
- [Original Word document](source/GAT-21-40.docx) and [conversion scripts/replay instructions](conversion-21-40/README.md).

This batch has 20 assignments, 175 main questions and 546 graphic placements: 435 formula images become LaTeX, 16 tables become editable Markdown/HTML, 89 drawings become SVG/JSON, and six originals containing raster artwork remain. All original EMFs, embedded PDFs and native equation records are preserved. The vector archive includes the 16 tables as well, for 105 raster-free vector scenes. Tables, 29 annotated-math drawings, four screenshot/data references and one flight network have additional structured records. Drawings remain review candidates; geometric constraints and animations are future work.

## Assignments 1–20

- [Read the formatted textbook](gat-1-20/GAT-1-20.html).
- [See highlighted changes in the textbook](gat-1-20/GAT-1-20-changes.html#new-network): yellow formula replacements are clickable comparisons; 115 blue diagram reconstructions appear beside their originals, with readable formulas for the ten annotated-math drawings.
- [Edit the Markdown and LaTeX](gat-1-20/GAT-1-20.md).
- [Review remaining conversion issues](gat-1-20/conversion-report.md) and [formula transcription notes](gat-1-20/formula-review.md).
- [Compare formulas with their source images](gat-1-20/formula-comparison.html).
- [Classify and review all textbook graphics](visual-pipeline/review.html), with a [reusable PDF inventory pipeline](visual-pipeline/README.md) and source-vector recovery and mathematical transcriptions.
- [Original Word document](source/GAT-1-20.doc).
- [Project context and future ideas](PROJECT-NOTES.md).
- [Python/JavaScript conversion scripts and replay instructions](conversion/README.md), including the image-recovery code and saved intermediate inputs.

The reading copy contains 20 assignments and 170 stable question anchors. It renders 546 formula placements from 220 distinct graphics as LaTeX and retains 120 diagram or instructional-image placements. All 336 recovered source graphics remain available for comparison. The original Word document's SHA-256 is recorded in `gat-1-20/manifest.json`.

The highlighted review copy now includes 115 diagram reconstruction candidates: four semantic networks, ten annotated-math drawings with structured entries/LaTeX, and 101 other vector drawings. Twelve coordinate diagrams also retain explicitly labelled mathematical coordinates. Only the calculator screenshot remains without a code reconstruction. The waveform in image1 is explicitly approximate; recovered drawing paths do not imply a solved geometry constraint model.

The HTML and its local assets are checked in, so reading the textbook requires no build step or external math service. Once this folder is deployed through the existing GitHub Pages site, its reading URL is `/sisley-math/gat-1-20/GAT-1-20.html`.

## Rebuild and check

From this folder, with a current Node.js installation:

```sh
npm ci --ignore-scripts
npm run build
npm run check
```

`build` renders all six batches with KaTeX and regenerates their browser pages and source comparisons. `check` verifies formula counts, image files, question anchors, local fonts, source glyphs, matrix rows and review references. Commit the regenerated HTML and assets with any content changes. Run `python3 conversion-21-40/scripts/verify_batch.py` for the 21–40 source-based checks; run `python3 conversion-batches/scripts/verify_batches.py` for 41–119 and `python3 -m unittest discover -s visual-pipeline/tests -v` for the existing visual pipeline.

The normal build starts with the checked-in Markdown. The separate `conversion/` archive preserves the legacy Word/image recovery scripts, the manually authored LaTeX mapping, dependency versions, and intermediate inputs needed to revisit that earlier work. Original wording, raised-minus notation, incomplete exercise entries, and apparent source errors are preserved. Review the linked notes before treating the material as fully proofread.

Third-party KaTeX fonts and styles retain their upstream license in `gat-1-20/assets/vendor/katex/LICENSE`.
