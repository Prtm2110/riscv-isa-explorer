from __future__ import annotations

import argparse
from pathlib import Path

from core import (
    INSTR_DICT_DEFAULT,
    build_shared_instruction_graph,
    find_multi_extension_instructions,
    group_by_extension,
    load_instr_dict,
)
from manual import clone_or_update_manual, collect_json_extensions, collect_manual_extensions, compare_extensions
from report import render_dot_graph, render_text_report


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="RISC-V instruction set explorer")
    parser.add_argument("--instr-dict", type=Path, default=INSTR_DICT_DEFAULT)
    parser.add_argument("--manual-dir", type=Path)
    parser.add_argument("--refresh-manual", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--graph-dot", type=Path)
    parser.add_argument(
        "--manual-cache-dir",
        type=Path,
        default=root / ".cache" / "riscv-isa-manual",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    instr_dict = load_instr_dict(args.instr_dict)
    grouped = group_by_extension(instr_dict)
    multi_extension = find_multi_extension_instructions(instr_dict)
    json_extensions = collect_json_extensions(instr_dict)

    manual_dir = args.manual_dir
    if manual_dir is None:
        manual_dir = clone_or_update_manual(args.manual_cache_dir, refresh=args.refresh_manual)

    manual_extensions = collect_manual_extensions(manual_dir)
    comparison = compare_extensions(json_extensions, manual_extensions)
    graph_edges = build_shared_instruction_graph(grouped)
    report = render_text_report(grouped, multi_extension, comparison, graph_edges)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    if args.graph_dot:
        args.graph_dot.write_text(render_dot_graph(graph_edges), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
