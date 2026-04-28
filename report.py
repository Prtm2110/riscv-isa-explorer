from __future__ import annotations

from manual import ExtensionComparison
from core import GraphEdge, MultiExtensionInstruction


def render_text_report(
    grouped: dict[str, list[str]],
    multi_extension: list[MultiExtensionInstruction],
    comparison: ExtensionComparison,
    graph_edges: list[GraphEdge],
) -> str:
    lines = ["Tier 1 Summary"]

    for tag in sorted(grouped):
        mnemonics = grouped[tag]
        lines.append(f"{tag} | {len(mnemonics)} instructions | e.g. {mnemonics[0]}")

    lines.append("")
    lines.append("Instructions In More Than One Extension")
    if multi_extension:
        for row in multi_extension:
            lines.append(f"{row.mnemonic} | {', '.join(row.tags)}")
    else:
        lines.append("None")

    lines.append("")
    lines.append("Tier 2 Cross Reference")
    lines.append(
        f"{len(comparison.matched)} matched, "
        f"{len(comparison.json_only)} in JSON only, "
        f"{len(comparison.manual_only)} in manual only"
    )

    lines.append("")
    lines.append("Extensions In JSON Only")
    lines.extend(comparison.json_only or ["None"])

    lines.append("")
    lines.append("Extensions In Manual Only")
    lines.extend(comparison.manual_only or ["None"])

    lines.append("")
    lines.append("Cross Reference Notes")
    lines.append("Some JSON-only names are internal-style tags from instr_dict.")
    lines.append("Some manual-only names are privileged or profile extensions that do not appear as instr_dict tags.")

    lines.append("")
    lines.append("Shared Instruction Graph")
    if graph_edges:
        for edge in graph_edges:
            lines.append(f"{edge.left} <-> {edge.right} ({edge.shared_count} shared)")
    else:
        lines.append("None")

    return "\n".join(lines) + "\n"


def render_dot_graph(graph_edges: list[GraphEdge]) -> str:
    lines = [
        "graph riscv_extensions {",
        '  graph [overlap=false];',
        '  node [shape=ellipse];',
    ]

    if not graph_edges:
        lines.append("}")
        return "\n".join(lines) + "\n"

    for edge in graph_edges:
        lines.append(
            f'  "{edge.left}" -- "{edge.right}" [label="{edge.shared_count}"];'
        )

    lines.append("}")
    return "\n".join(lines) + "\n"
