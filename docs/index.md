# RISC-V Instruction Set Explorer

This project reads RISC-V instruction data, groups instructions by extension, cross-checks those extensions against the official ISA manual, and generates a shared-instruction graph.

It covers:

- Tier 1 parsing from `instr_dict.json`
- Tier 2 cross-reference against the official RISC-V ISA manual
- unit tests
- a text-based shared-instruction graph
- optional Graphviz DOT export

## Quick Start

Run the program:

```bash
python3 main.py
```

Run the tests:

```bash
python3 -m unittest discover -s tests
```

Build the docs site:

```bash
python3 -m pip install -r requirements-docs.txt
mkdocs build
```

## Graph Preview

The graph connects extension tags that share at least one instruction.
Each edge label is the number of shared instructions.

<div class="graph-preview graph-panel">
  <img
    src="assets/generated/sample_graph.svg"
    alt="RISC-V extension graph showing shared instructions between extensions"
    class="graph-image"
  />
</div>

## Repository Contents

- `main.py` for CLI orchestration
- `core.py` for Tier 1 logic
- `manual.py` for Tier 2 matching logic
- `report.py` for report rendering
- `data/instr_dict.json` for the vendored input data
- `tests/` for unit tests

## Project Notes

The repository focuses on the final project deliverable, checked-in sample artifacts, tests, and the docs site.
