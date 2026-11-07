# GAT Assignments 1–20

Open [the browser textbook](GAT-1-20.html) for a formatted, offline reading copy, or [the Markdown textbook](GAT-1-20.md) for editing. Keep this folder intact so its local images and math fonts resolve.

- [GAT-1-20.md](GAT-1-20.md): all 20 assignments, with 170 stable question anchors.
- [GAT-1-20.html](GAT-1-20.html): the same textbook with LaTeX rendered as HTML and accessible MathML.
- [formula-review.md](formula-review.md): first-pass transcription choices and remaining issues by reference page.
- [formula-comparison.html](formula-comparison.html): all 220 converted graphics beside their LaTeX transcriptions.
- [formula-transcriptions.json](formula-transcriptions.json): the decision for every one of the 336 graphics, including LaTeX, placements, questions, and reference pages.
- [conversion-report.md](conversion-report.md): remaining issues by reference page, with assignment/question links. Reference pagination differs from the original file's saved page count.
- [manifest.json](manifest.json): source hash, assignment/question IDs, image occurrences, reference pages, dimensions, and issue flags.
- `assets/`: all 336 recovered graphics retained for provenance. The textbook now uses 116 of them in 120 image placements; 220 graphics in 546 placements have been replaced with LaTeX.
- `assets/originals/`: all 336 extracted legacy PICT/EMF graphics, unchanged from the Word import.
- `assets/equations-png/`: high-resolution PNG copies of the 212 original SVG equations.
- `assets/vendor/katex/`: local math styles, fonts, version, and license for offline HTML reading.

The Markdown uses `$...$` and `$$...$$` for LaTeX, plus inline HTML for image dimensions, emphasis, superscripts, and subscripts. Use a Markdown renderer with math and inline HTML support. The HTML copy already includes rendered math and does not require a Markdown extension or internet connection.

Some equations were recovered from their original drawing instructions because ordinary Word conversion changed fonts, omitted figures, or misread image dimensions. Those equations are now editable LaTeX. Original raised-minus notation, wording, and apparent source typos are preserved. See the reports before publishing exercises with flagged notation, labels, or matrix entries. The file also references 10 separate classroom sketch sheets that are not included.

To rebuild the HTML after editing the Markdown, run `npm ci --ignore-scripts` and `npm run build` from the project root. Run `npm run check` to check the generated textbook against the transcription records. The renderer and exact dependency versions are in the accompanying `scripts/`, `package.json`, and `package-lock.json`.

The source document was not modified. This package contains the transcription and assets; it does not implement executable assignments or progress storage. Question IDs such as `gat-01-iii` can later identify progress records independently of page layout.
