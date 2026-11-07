# Textbook visual preservation pipeline

Preserve the source, classify each visual, create a machine-readable candidate, then compare it with the source before using it in the textbook. The pipeline brings the GAT work into one catalog and supplies local PDF inventory, source-vector recovery, mathematical transcription, and classification-review workflows.

Read [the textbook with highlighted comparisons](../gat-1-20/GAT-1-20-changes.html#diagram-image279-1), or use [the visual inventory](review.html) for classification work. All 336 source graphics and 666 placements remain recorded: 220 existing LaTeX assets, 115 diagram reconstruction candidates, and one calculator screenshot retained as an image. The 115 candidates comprise four semantic network scenes and 111 recovered vector scenes (including ten annotated-math scenes). One pair of source PNGs is byte-identical. Candidates appear in 119 textbook placements beside their originals; the regular reading copy retains the original diagrams.

## What works now

- Versioned, extensible [category definitions](taxonomy.json), including formulas and all ten retained-image categories, plus tables, text, compound figures, scans, illustrations and unknowns.
- [GAT catalog](gat-catalog.json) with source hashes, original files, duplicate references, page/question occurrences, classifications, conversion states and unresolved issues.
- PDF inventory of embedded raster placements and nearby vector groups, rendered crops, full-page previews with region overlays, and positioned text/vector drawing commands. Additional manually specified regions can include native-text formulas or compound figures.
- An offline review page with category/state/search filters, original/candidate comparisons and downloadable classification decisions. No server, account or network service is required.
- Reviewed decisions are bound to both the source-document hash and image hash; invalid or stale decisions do not overwrite the catalog.
- Existing LaTeX is imported as editable text. New LaTeX candidates can be supplied in a decision file. The existing textbook renderer remains responsible for KaTeX validation and HTML/MathML rendering.
- Four data-only directed multigraph scenes, SVG rendering and adjacency-matrix export, preserving loops and parallel edges.
- 111 editable SVG/JSON drawing scenes recovered from the saved vector atlas, with stable element IDs, source drawing primitives and extracted text. No candidate SVG embeds a raster image.
- Nine annotated matrices and one calculation-flow diagram with transcribed entries, explicit blanks, annotation relationships and LaTeX exports. The highlighted textbook exposes these through **Show readable formulas**.
- Twelve coordinate diagrams with source-labelled coordinates, visible right-angle markers where present, and the explicitly labelled reflection in image327. Unlabelled coordinates remain unknown.

**This is an assisted preservation pipeline, not a trained automatic image classifier or general OCR engine.** The existing GAT classifications are imported from the prior visual review. New PDF candidates start unclassified, except that a page-sized raster is tentatively labelled as a scan. A reviewer (human or an assistant inspecting the actual images and page context) supplies category decisions and transcriptions. No external service receives the source material.

## Run it

Use Python 3.10+ in a virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r visual-pipeline/requirements.txt
```

Commands below run from the parent `sisley-math/` folder (or the original workspace root). Substitute your environment's Python executable if necessary.

Inventory a PDF into a new output directory:

```sh
.venv/bin/python visual-pipeline/pipeline.py ingest-pdf textbook.pdf working/book-01
.venv/bin/python visual-pipeline/pipeline.py report working/book-01/catalog.json working/book-01/review.html
```

`--pages 1,2,3` processes a subset and records that incomplete coverage explicitly. `--dpi 144` is the default. The output retains a byte-for-byte copy of the PDF and refuses to overwrite an existing directory.

The PDF importer follows [pdfplumber's documented image, vector, text and crop APIs](https://github.com/jsvine/pdfplumber#the-pdfplumberpage-class). Coordinates use PDF points; generic PDF regions use `(x0, top, x1, bottom)` in the page's top-left coordinate system. The imported GAT manifest retains its original bottom-left bounding boxes and labels that coordinate system explicitly. Do not mix these coordinate systems without a page-height/origin transform.

For extra regions, create JSON such as:

```json
[{"page": 1, "bbox_pt": [90, 275, 535, 370]}]
```

Pass it as `--regions regions.json` during a fresh import. Regions are additional candidates, so they can overlap automatically detected fragments. Grouping fragments, splitting compound figures, and certifying page completeness are review tasks, not implemented automatic decisions. This initial importer does not OCR scans or detect native-text formulas. Its crops can contain neighbouring content; it preserves the complete PDF and full-page previews for comparison.

Review and save classifications:

1. Open `review.html`, filter by category or conversion state, and inspect the source and page context.
2. Expand **Review classification**, choose a category, add evidence/ambiguity notes, then **Queue decision**.
3. Enter a reviewer name and **Export decisions**. Edits live only in the current tab until exported.
4. Apply the downloaded file and regenerate the report:

```sh
.venv/bin/python visual-pipeline/pipeline.py apply working/book-01/catalog.json visual-decisions.json
.venv/bin/python visual-pipeline/pipeline.py report working/book-01/catalog.json working/book-01/review.html
```

No report operation silently marks a conversion faithful or a page complete. The file format is deliberately plain JSON so an image-reading assistant can produce the same review patches without using the UI.

## Representation and review contract

An asset stores its immutable source image and hash, classification and conversion. A placement stores its page, bounding box, coordinate system and optional question ID. Duplicate images share meaning only after review; the GAT import preserves original asset IDs even for the exact duplicate. PDF imports deduplicate identical rendered RGB crops while retaining each occurrence.

Classification states are `unclassified`, `proposed`, `reviewed`. Conversion states are independently `unconverted`, `candidate`, `converted`, with a separate fidelity review of `needs_review` or `verified`. A verified conversion requires written `review_evidence`. The legacy LaTeX is `converted` but still `needs_review`: syntax/glyph checks do not establish complete mathematical proofreading. The validator checks implemented fields and local references; this is a version-1 format, not a public API stability promise.

An assistant or converter can submit this decision shape:

```json
{
  "document_sha256": "copy from the catalog",
  "reviewer": "reviewer or tool and version",
  "assets": [{
    "id": "copy asset ID",
    "sha256": "copy asset hash",
    "category": "formula",
    "notes": "Describe what was checked and any ambiguity.",
    "conversion": {
      "status": "candidate",
      "kind": "latex",
      "latex": "x^{2}+y^{2}=r^{2}",
      "review": "needs_review"
    }
  }]
}
```

`apply` validates structure, hashes and references, not the mathematical correctness or LaTeX syntax of a new transcription. Never mark a candidate verified solely because it parses. Unknown symbols, illegible entries and apparent source errors stay documented; they must not be silently guessed or corrected. A compound figure can retain the original while its individual parts are transcribed in future component records.

## Graphics as code

The long-term representation should capture meaning separately from drawing style:

| Visual | Semantic representation | Drawing representation | Implementation today |
|---|---|---|---|
| Formula | LaTeX; later an explicit expression tree where unambiguous | HTML/MathML via existing KaTeX build | Existing transcriptions imported |
| Network/map | Node IDs, directed edges, multiplicity, optional weights | Node positions and edge control points → SVG | Directed multigraph renderer implemented |
| Coordinate plot | Source-labelled points and marked givens; unknown values stay unknown | Recovered SVG paths | Twelve drawing scenes plus coordinate-givens records; live plot renderer remains future work |
| Geometry/transformation | Drawing paths/positions and extracted labels; constraint models need further authoring | Recovered SVG scene | Source vectors preserved; no general geometry solver or inferred constraints |
| Annotated matrix/calculation | Entries/expressions plus annotation relationships | Preserved SVG layout plus readable LaTeX panels | Ten scenes transcribed; changing semantic entries does not yet reflow the preserved source layout |
| Table | Cells, headers, units and explicit blanks | HTML table | Category and conversion target only |
| Screenshot/illustration | Transcript/description where useful | Original image retained | Category and conversion target only |

An exact equation cannot be recovered from the appearance of a plotted curve alone. Store a traced approximation as an approximation; promote it to an exact function only when the source states one. Likewise, a line that looks perpendicular is not a mathematical constraint unless the source states or marks it. Store stated givens, visual estimates and later learner-created parameters separately.

### Working network example

[image262.scene.json](examples/image262.scene.json) transcribes five nodes and ten directed edges, including two edges from node 1 to node 3. Coordinates and Bézier controls are approximate layout values; graph connectivity is independent of them. The original image stays in the textbook.

```sh
.venv/bin/python visual-pipeline/pipeline.py render-network visual-pipeline/examples/image262.scene.json visual-pipeline/examples/image262.svg --adjacency visual-pipeline/examples/image262.adjacency.json
```

Edit a node position to change the drawing without changing the adjacency matrix. Edit an edge endpoint to change the mathematics. This is the foundation for future programmable graphics; animation controls, learner code execution, a geometry solver and a custom language are not implemented.

The network scene supports explicit node IDs/labels, finite drawing positions, directed edges with independent IDs, optional quadratic/cubic controls and arrow positions. `image279`, `image308` and `image329` have matching scene/SVG/adjacency files in `examples/`. Their edge counts are 10, 9 and 10 respectively; image329 includes a loop and three parallel edges from node 1 to node 3. No arbitrary executable code is evaluated.

### Source-vector recovery and mathematical records

`recover_vectors.py` reads the saved `conversion/checkpoints/atlas.pdf` and its metadata. It uses Poppler `pdftocairo` (validated with 26.05.0) to recover drawing commands and font outlines, matches the original PNG crop precisely, and saves a versioned scene plus SVG. `vector_scene.py` rebuilds the SVG from the JSON and rejects raster, script and external-resource elements. Positioned PDF labels are searchable in JSON; legacy glyph encodings may need correction before using those extracted labels as semantic text. Font outlines in the visible SVG preserve the original appearance.

`annotated-math.json` supplies the reviewed transcriptions for ten diagrams, while `coordinate-givens.json` supplies explicit mathematical coordinates/givens for twelve plots. Source drawing coordinates are PDF layout points, not mathematical coordinates. The SVG tree and mathematical records are deliberately separate: editing a network node updates its SVG through the network renderer, but changing a matrix value or a coordinate-given record does **not** yet automatically relayout the preserved SVG drawing. The corresponding matrix LaTeX exports do reflect semantic entry changes after rebuilding.

Two source-specific recovery cases are documented in the scene notes: image1 uses a raster-centreline trace with 0.20-point simplification tolerance (an approximation, not an exact sine function), and image253 replaces three uniform one-pixel swatches with equivalent SVG rectangles. Image15 is a calculator screenshot and remains unconverted.

With Poppler installed and `pdftocairo` on PATH, regenerate from the preserved repository folder:

```sh
.venv/bin/python visual-pipeline/recover_vectors.py conversion/checkpoints
.venv/bin/python visual-pipeline/pipeline.py render-vector visual-pipeline/reconstructions/image218.scene.json visual-pipeline/reconstructions/image218.svg --math visual-pipeline/reconstructions/image218.math.json
npm run build
npm run check
```

Use `--pdftocairo /path/to/pdftocairo` if it is not on PATH. The recovery script is specific to this saved GAT atlas; the generic PDF inventory command remains separate. `npm run build` copies the current reconstructed SVGs and readable math into the portable textbook folder. The bundled `diagram-conversions.json` supports historical textbook replay without requiring the separate inventory folder.

## Reproduce and validate the GAT inventory

Use a fresh catalog name when reimporting; import refuses to overwrite existing decisions:

```sh
.venv/bin/python visual-pipeline/pipeline.py import-gat gat-1-20 visual-pipeline/gat-retained-categories.json visual-pipeline/gat-catalog-fresh.json
.venv/bin/python visual-pipeline/pipeline.py apply visual-pipeline/gat-catalog-fresh.json visual-pipeline/reconstruction-decisions.json
.venv/bin/python visual-pipeline/pipeline.py validate visual-pipeline/gat-catalog-fresh.json
.venv/bin/python visual-pipeline/pipeline.py report visual-pipeline/gat-catalog-fresh.json visual-pipeline/review.html
.venv/bin/python -m unittest discover -s visual-pipeline/tests -v
```

The checked-in `gat-catalog.json` already includes all 115 reconstruction candidates. Relative asset references resolve from the catalog's directory. A copied catalog must keep that directory relationship or update the paths. Changes to the source assets are detected by hash checks. After reviewing or editing a scene, rerun its renderer and regenerate the report.

Validation: all 336 source hashes and 666 placements; 17 tests covering source integrity, transactional review decisions, graph multiplicity/loops, correspondence between graphs and the printed adjacency matrix, a reflection matrix identity, explicit exercise blanks, tiny matrix entries checked against positioned source glyphs, and rejection of raster/executable SVG content. All 115 reconstructed SVGs were rasterized and their source/candidate pairs inspected on 15 comparison sheets. Pixel-overlap diagnostics are retained in `reconstruction-verification.json`; very thin strokes differ through antialiasing, and the hand-redrawn networks intentionally use approximate layouts. All 119 blue comparisons, 546 yellow formula comparisons and ten readable-math panels have valid references. The earlier generic PDF import was tested on reference pages 1–3. Re-running recovery reproduced all 233 scene/SVG/math/report files byte-for-byte, and the catalog import plus decision replay matched exactly. Report JavaScript is syntax-checked; the browser review controls have not yet undergone interactive browser QA. The source/reference PDF remains subject to the original conversion notes about pagination and rendering.

## Next increments

1. Review missing/compound regions page by page and add explicit parent/child regions and a page-completeness checklist.
2. Add an optional vision/OCR proposal adapter that emits the same hash-bound decisions, with evidence and uncertainty. Evaluate it against reviewed assets before trusting bulk classifications; keep classification quality separate from transcription quality.
3. Link semantic matrix/coordinate records to layout renderers; build explicit geometry constraint models without inferring facts from pixel positions. Approve source fidelity before enabling learner edits.
4. After faithful reproduction is approved, add learner-editable parameters, constraints and animation. Learner changes should produce a separate version, preserving the source-faithful edition.
