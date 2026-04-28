# Usage

## Basic Command

```bash
python3 main.py
```

This prints the Tier 1 summary, the multi-extension instruction list, the Tier 2 cross-reference summary, and the shared-instruction graph.

## Useful Options

Use a local ISA manual checkout:

```bash
python3 main.py --manual-dir /path/to/riscv-isa-manual
```

Refresh the cached manual clone:

```bash
python3 main.py --refresh-manual
```

Write the text report to a file:

```bash
python3 main.py --output sample_output.txt
```

Write the graph as DOT:

```bash
python3 main.py --graph-dot sample_graph.dot
```

## Test Command

```bash
python3 -m unittest discover -s tests
```
