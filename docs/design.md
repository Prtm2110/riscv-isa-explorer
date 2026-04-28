# Design

## Code Structure

The project stays small on purpose.

- `main.py` wires the CLI together
- `core.py` handles instruction parsing, grouping, and graph edges
- `manual.py` handles ISA manual fetching, token extraction, normalization, and comparison
- `report.py` renders the text report and DOT graph

This split keeps each file focused without turning the project into a heavy package.

## Tier 1 Choices

- Raw JSON extension tags are preserved in the Tier 1 summary.
- Mnemonics are derived from JSON keys by converting `_` to `.` and uppercasing.
- Instructions with more than one extension are listed explicitly.

## Tier 2 Choices

- Comparison uses a separate normalization step.
- Known mappings like `rv_zba -> zba` are handled directly.
- Composite tags such as `rv_d_zfa` split into more than one extension token.
- `rv_zicbo` is resolved by instruction mnemonic so `CBO.ZERO` maps differently from the other `CBO.*` instructions.

## Known Limits

- Some JSON tags are internal-style names, so JSON-only output is expected.
- The ISA manual includes privileged and profile extensions that do not appear as direct instruction tags in `instr_dict.json`.
