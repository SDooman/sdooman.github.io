# Formula conversion review

Reviewed all **336 distinct embedded graphics**. Converted **220 formula or mathematical-table images**, covering **546 placements**, to editable LaTeX. The textbook retains **116 distinct images in 120 placements** for diagrams, graphs, calculator screens, and annotated instructional figures.

All 212 SVG equation images were converted, along with 8 PNG graphics containing formulas, symbols, or labelled matrices. Every source image is still retained for comparison.

- [Read the textbook](GAT-1-20.md).
- [Compare each transcription with its source image](formula-comparison.html).
- [Machine-readable transcriptions and image decisions](formula-transcriptions.json) include source filenames, question IDs, and reference pages for every graphic.

## Items to review by reference page

Page numbers refer to the existing 94-page reference render, not verified original Word pagination.

| Reference page | Question | Remaining issue |
| --- | --- | --- |
| 19 | [5 I](GAT-1-20.md#gat-05-i) | The “combining the stages” expression has unusual composition notation and a missing closing parenthesis. Transcribed as written; needs proofreading. [Source comparison](formula-comparison.html#image96). |
| 20 | [5 I](GAT-1-20.md#gat-05-i) | The final coordinate-like expression uses a period in “−15.0” rather than a comma. Preserved as written. [Source comparison](formula-comparison.html#image104). |
| 62 | [13 VII](GAT-1-20.md#gat-13-vii) | The labelled matrix figure has extremely small entries. Kept as an image rather than guessing. |
| 65 | [14 V](GAT-1-20.md#gat-14-v) | The matrix explanation uses boxes and arrows, with tiny entries. Kept as an image. |
| 70 | [15 VI](GAT-1-20.md#gat-15-vi) | The annotated matrix multiplication figure has tiny entries. Kept as an image. |
| 74 | [16 V](GAT-1-20.md#gat-16-v) | The annotated matrix multiplication figure has tiny entries. Kept as an image. |
| 85 | [19 I](GAT-1-20.md#gat-19-i) | The matrix illustration uses arrows and boxed rows/columns; segmented brackets remain in the retained image. |
| 90 | [20 I](GAT-1-20.md#gat-20-i) | The blank-column matrix illustrations use arrows and labels; segmented brackets remain in the retained images. |
| 93 | [20 V](GAT-1-20.md#gat-20-v) | The illustration labels the order of three matrices using arrows; segmented brackets remain in the retained image. |

Other small diagram labels and missing classroom worksheets are listed in the [original conversion notes](conversion-report.md).

## Transcription choices

- The source's raised negative sign is written as `{}^{-}` in LaTeX. It has not been replaced with ordinary subtraction notation.
- Calculator square-root key symbols use `\surd`; complete radical expressions use `\sqrt{...}`.
- Blank exercise entries remain blank. The incomplete 5-by-5 matrix still has fifteen missing entries; `\phantom{0}` reserves their space without supplying answers.
- Three labelled matrix graphics are now labelled LaTeX arrays. Their labels and values are preserved; their print framing is simplified.
- The centered-dot graphic remains `\cdot`, including where the source reads it as “by” for matrix dimensions.
- Multiple-choice distractors and apparent source errors were not mathematically corrected.

## Rendering and validation

The Markdown uses `$...$` for inline formulas and `$$...$$` for display formulas. It requires a Markdown viewer with math support. The companion HTML pre-renders the same LaTeX using KaTeX and includes local fonts, so no network connection or JavaScript is needed to read it.

Every transcription was checked for valid LaTeX. Formula placements, retained image links, question anchors, source glyph counts, and matrix row contents were checked against the conversion records. This is a first transcription pass, not a mathematical answer-key audit.
