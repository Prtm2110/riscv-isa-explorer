from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOT_PATH = ROOT / "artifacts" / "sample_graph.dot"
SVG_PATH = ROOT / "artifacts" / "sample_graph.svg"
DOCS_SVG_PATH = ROOT / "docs" / "assets" / "generated" / "sample_graph.svg"


def main() -> int:
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["dot", "-Tsvg", str(DOT_PATH), "-o", str(SVG_PATH)],
        check=True,
    )
    DOCS_SVG_PATH.write_text(SVG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
