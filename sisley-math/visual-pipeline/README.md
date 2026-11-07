# Textbook visual preservation pipeline

Preserve the source, classify each visual, create a machine-readable candidate, then compare it with the source before using it in the textbook. This first implementation brings the existing GAT work into one catalog and supplies a local PDF inventory and classification-review workflow.

Open [the visual review page](review.html). It includes all 336 GAT source graphics and 666 placements: 220 formula assets already transcribed to LaTeX, plus the 116 retained image assets. One pair of retained PNGs is byte-identical. The network reconstruction is a candidate; it does not replace the textbook image.

## What works now

- Versioned, extensible [category definitions](taxonomy.json), including formulas and all ten retained-image categories, plus tables, text, compound figures, scans, illustrations and unknowns.
- [GAT catalog](gat-catalog.json) with source hashes, original files, duplicate references, page/question occurrences, classifications, conversion states and unresolved issues.
- PDF inventory of embedded raster placements and nearby vector groups, rendered crops, full-page previews with region overlays, and positioned text/vector drawing commands. Additional manually specified regions can include native-text formulas or compound figures.
- An offline review page with category/state/search filters, original/candidate comparisons and downloadable classification decisions. No server, account or network service is required.
- Reviewed decisions are bound to both the source-document hash and image hash; invalid or stale decisions do not overwrite the catalog.
- Existing LaTeX is imported as editable text. New LaTeX candidates can be supplied in a decision file. The existing textbook renderer remains responsible for KaTeX validation and HTML/MathML rendering.
- A data-only directed multigraph representation, SVG renderer and adjacency-matrix exporter. Loops and parallel edges are supported.

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
| Coordinate plot | Axis scales/units, labelled points, known expressions or sampled traces | SVG plot with adjustable view | Category and conversion target only |
| Geometry/transformation | Points, segments, named transformations, explicit constraints/givens | SVG scene | Category and conversion target only |
| Annotated matrix/calculation | Entries/expressions plus annotation relationships | LaTeX with a separate layout layer | Category and conversion target only |
| Table | Cells, headers, units and explicit blanks | HTML table | Category and conversion target only |
| Screenshot/illustration | Transcript/description where useful | Original image retained | Category and conversion target only |

An exact equation cannot be recovered from the appearance of a plotted curve alone. Store a traced approximation as an approximation; promote it to an exact function only when the source states one. Likewise, a line that looks perpendicular is not a mathematical constraint unless the source states or marks it. Store stated givens, visual estimates and later learner-created parameters separately.

### Working network example

[image262.scene.json](examples/image262.scene.json) transcribes five nodes and ten directed edges, including two edges from node 1 to node 3. Coordinates and Bézier controls are approximate layout values; graph connectivity is independent of them. The original image stays in the textbook.

```sh
.venv/bin/python visual-pipeline/pipeline.py render-network visual-pipeline/examples/image262.scene.json visual-pipeline/examples/image262.svg --adjacency visual-pipeline/examples/image262.adjacency.json
```

Edit a node position to change the drawing without changing the adjacency matrix. Edit an edge endpoint to change the mathematics. This is the foundation for future programmable graphics; animation controls, learner code execution, a geometry solver and a custom language are not implemented.

The scene supports explicit node IDs/labels, finite drawing positions, directed edges with independent IDs, optional quadratic/cubic controls and arrow positions. No arbitrary executable code is evaluated. Other scene kinds are rejected until a corresponding validator/renderer exists.

## Reproduce and validate the GAT inventory

Use a fresh catalog name when reimporting; import refuses to overwrite existing decisions:

```sh
.venv/bin/python visual-pipeline/pipeline.py import-gat gat-1-20 visual-pipeline/gat-retained-categories.json visual-pipeline/gat-catalog-fresh.json
.venv/bin/python visual-pipeline/pipeline.py apply visual-pipeline/gat-catalog-fresh.json visual-pipeline/examples/image262.decision.json
.venv/bin/python visual-pipeline/pipeline.py validate visual-pipeline/gat-catalog-fresh.json
.venv/bin/python visual-pipeline/pipeline.py report visual-pipeline/gat-catalog-fresh.json visual-pipeline/review.html
.venv/bin/python -m unittest discover -s visual-pipeline/tests -v
```

The checked-in `gat-catalog.json` already includes the network candidate. Relative asset references resolve from the catalog's directory. A copied catalog must keep that directory relationship or update the paths. Changes to the source assets are detected by hash checks. After reviewing or editing a scene, rerun its renderer and regenerate the report.

Validation performed for this initial version: all 336 source hashes and 666 placement references; eight tests covering stale decisions, transactional updates, duplicate placements, grouping, graph multiplicity/loops and separation of layout from connectivity; ingestion of reference PDF pages 1–3 with rendered-region inspection. Report JavaScript is syntax-checked; the browser review controls have not yet undergone interactive browser QA. The source/reference PDF remains subject to the original conversion notes about pagination and rendering.

## Next increments

1. Review missing/compound regions page by page and add explicit parent/child regions and a page-completeness checklist.
2. Add an optional vision/OCR proposal adapter that emits the same hash-bound decisions, with evidence and uncertainty. Evaluate it against reviewed assets before trusting bulk classifications; keep classification quality separate from transcription quality.
3. Implement annotated-math and geometry/plot converters, each with source comparison and category-specific checks.
4. After faithful reproduction is approved, add learner-editable parameters, constraints and animation. Learner changes should produce a separate version, preserving the source-faithful edition.
