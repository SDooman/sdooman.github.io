# Sisley math textbook preservation

This folder preserves the first 20 GAT assignments from the supplied high-school math textbook, including the original Word document, editable Markdown and LaTeX, recovered graphics, an offline browser reading copy, and conversion records.

- [Read the formatted textbook](gat-1-20/GAT-1-20.html).
- [Edit the Markdown and LaTeX](gat-1-20/GAT-1-20.md).
- [Review remaining conversion issues](gat-1-20/conversion-report.md) and [formula transcription notes](gat-1-20/formula-review.md).
- [Compare formulas with their source images](gat-1-20/formula-comparison.html).
- [Original Word document](source/GAT-1-20.doc).
- [Project context and future ideas](PROJECT-NOTES.md).
- [Python/JavaScript conversion scripts and replay instructions](conversion/README.md), including the image-recovery code and saved intermediate inputs.

The reading copy contains 20 assignments and 170 stable question anchors. It renders 546 formula placements from 220 distinct graphics as LaTeX and retains 120 diagram or instructional-image placements. All 336 recovered source graphics remain available for comparison. The original Word document's SHA-256 is recorded in `gat-1-20/manifest.json`.

The HTML and its local assets are checked in, so reading the textbook requires no build step or external math service. Once this folder is deployed through the existing GitHub Pages site, its reading URL is `/sisley-math/gat-1-20/GAT-1-20.html`.

## Rebuild and check

From this folder, with a current Node.js installation:

```sh
npm ci --ignore-scripts
npm run build
npm run check
```

`build` renders the Markdown with KaTeX and regenerates the browser pages and source comparison. `check` verifies formula counts, image files, question anchors, local fonts, source glyphs, and matrix rows. Commit the regenerated HTML and assets with any content changes.

The normal build starts with the checked-in Markdown. The separate `conversion/` archive preserves the legacy Word/image recovery scripts, the manually authored LaTeX mapping, dependency versions, and intermediate inputs needed to revisit that earlier work. Original wording, raised-minus notation, incomplete exercise entries, and apparent source errors are preserved. Review the linked notes before treating the material as fully proofread.

Third-party KaTeX fonts and styles retain their upstream license in `gat-1-20/assets/vendor/katex/LICENSE`.
