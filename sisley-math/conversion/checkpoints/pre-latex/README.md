# GAT Assignments 1–20

Open [the Markdown textbook](GAT-1-20.md). Keep this folder intact so its local images resolve.

- [GAT-1-20.md](GAT-1-20.md): all 20 assignments, with 170 stable question anchors.
- [conversion-report.md](conversion-report.md): remaining issues by reference page, with assignment/question links. Reference pagination differs from the original file's saved page count.
- [manifest.json](manifest.json): source hash, assignment/question IDs, image occurrences, reference pages, dimensions, and issue flags.
- `assets/`: 212 SVG equation images and 124 PNG graphics, used in all 666 detected image placements.
- `assets/originals/`: all 336 extracted legacy PICT/EMF graphics, unchanged from the Word import.
- `assets/equations-png/`: high-resolution PNG fallbacks for the 212 SVG equations.

The Markdown uses inline HTML for image dimensions, emphasis, superscripts, and subscripts. Use a Markdown renderer that allows these elements. SVG equations have their own intrinsic dimensions. For inline equations in a browser, `img { vertical-align: middle; max-width: 100%; }` is a useful starting style.

Some equations were recovered from their original drawing instructions because ordinary Word conversion changed fonts, omitted figures, or misread image dimensions. Their text remains in SVG images rather than semantic LaTeX. Original raised-minus notation, wording, and apparent source typos are preserved. See the report before publishing exercises with flagged labels or matrix entries. The file also references 10 separate classroom sketch sheets that are not included.

The source document was not modified. This package contains the transcription and assets; it does not implement executable assignments or progress storage. Question IDs such as `gat-01-iii` can later identify progress records independently of page layout.
