# RISC-V Instruction Set Explorer

This project reads RISC-V instruction data, groups instructions by extension, cross-checks those extensions against the official ISA manual, and generates a shared-instruction graph.

GitHub Pages: https://prtm2110.github.io/riscv-isa-explorer/

## Graph Preview

![RISC-V extension graph showing shared instructions between extensions](artifacts/sample_graph.svg)

The graph connects extension tags that share at least one instruction.
Each edge label is the number of shared instructions.

- [View the docs site](https://prtm2110.github.io/riscv-isa-explorer/)
- [View the results page](https://prtm2110.github.io/riscv-isa-explorer/results/)
- [Open the DOT artifact](artifacts/sample_graph.dot)

## Requirements

- Python 3.13 or newer

## Run

```bash
python3 main.py
```

Useful options:

```bash
python3 main.py --refresh-manual
python3 main.py --manual-dir /path/to/riscv-isa-manual
python3 main.py --output artifacts/sample_output.txt
python3 main.py --graph-dot artifacts/sample_graph.dot
```

## Run Tests

```bash
python3 -m unittest discover -s tests
```

## Docs Site

Install docs dependencies:

```bash
python3 -m pip install -r requirements-docs.txt
```

Preview locally:

```bash
mkdocs serve
```

Build the site:

```bash
mkdocs build
```

GitHub Pages deployment is handled by the workflow in `.github/workflows/docs.yml`.
The docs site includes an embedded graph view.

## Project Layout

- `main.py` runs the CLI
- `core.py` handles Tier 1 parsing and graph data
- `manual.py` handles ISA manual fetching and Tier 2 matching
- `report.py` renders text and DOT output
- `data/instr_dict.json` is the vendored instruction data source
- `tests/` contains the unit tests
- `docs/` contains the MkDocs site

## Design Decisions

- The code stays flat at the repository root because the project is small.
- Tier 1 reports raw extension tags exactly as stored in `instr_dict.json`.
- Tier 2 uses a separate normalization step so JSON tags and manual extension names can match cleanly.
- The graph is available both as plain text in the report and as an optional `.dot` file.

## Assumptions And Known Limits

- `rv_zicbo` is split by instruction name:
  - `CBO.ZERO` maps to `zicboz`
  - the other `CBO.*` instructions map to `zicbom`
- Composite tags like `rv_d_zfa` are treated as more than one manual extension when comparing names.
- Some JSON-only names are internal-style tags, so unmatched items are expected.
- The ISA manual contains privileged and profile extensions that do not appear as direct instruction tags in `instr_dict.json`.

## Sample Artifacts

- [artifacts/sample_output.txt](artifacts/sample_output.txt)
- [artifacts/sample_graph.dot](artifacts/sample_graph.dot)
- [artifacts/sample_graph.svg](artifacts/sample_graph.svg)
