# Project context

## Intended goal

Reproduce this textbook and other materials from the user's high-school math class as a browser-based learning platform.

The user's initial ideas are:

- Render the questions as Markdown, using LaTeX for formulas and preserving diagrams.
- Turn programming assignments into computations that learners can write and execute in the browser. A custom programming language is an idea to explore, not a decided requirement.
- Save progress locally, with user accounts as a possible later addition.

## Preserved work

The first source is `source/GAT-1-20.doc`, originally named `GAT 1-20.doc`. Its 20 assignments are converted to `gat-1-20/GAT-1-20.md` and an offline HTML reading copy.

- 170 stable question identifiers, such as `gat-01-iii`, can later identify progress records independently of pagination.
- All 336 distinct embedded graphics were reviewed and retained in recovered form, alongside their extracted legacy PICT/EMF originals.
- 220 formula or mathematical-table graphics, appearing 546 times, were transcribed into LaTeX.
- 116 distinct diagrams and instructional graphics remain images in 120 placements.
- `manifest.json` maps the source, questions, image occurrences, reference pages, and LaTeX representations.
- `formula-transcriptions.json` records the conversion decision for every graphic. `formula-comparison.html` displays all converted formulas beside their retained source images.
- The build uses pinned Marked and KaTeX dependencies. Generated HTML, math fonts, and styles are stored locally for offline reading.
- `conversion/` preserves the Python and JavaScript recovery/transcription scripts, their dependency versions, and the imported DOCX, size-corrected DOCX/PDF, diagram atlas, extracted metadata, and pre-LaTeX baseline. Its README describes isolated replay and document-specific assumptions.

## Known limitations

- The Word file's saved metadata reports 87 pages. A size-corrected reference render has 94 pages; original printed page boundaries are unverified. Review notes use those reference pages.
- Two expressions in Assignment 5, on reference pages 19–20, need mathematical proofreading. Their apparent source errors were preserved.
- Some retained instructional diagrams have tiny labels or matrix entries and segmented brackets. The reports list affected reference pages.
- Ten separate classroom sketch sheets are referenced but were not included in the supplied file.
- LaTeX makes the formulas editable and renderable; it is not an executable mathematical model or answer key.
- Interactive computations, grading, progress storage, and user accounts have not been implemented.

## Suggested continuation

Resolve the flagged formulas and diagram labels, obtain the missing sketch sheets, and preserve additional textbook sections using the same question IDs and source records. A later platform prototype can build on this content with a browser computation environment and local progress storage. These are future ideas rather than implemented features or fixed technology choices.
