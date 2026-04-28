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
    lines.append(f"{len(comparison.matched)} direct matches")
    lines.append(f"{len(comparison.json_only)} JSON-only extension names")
    lines.append(f"{len(comparison.json_internal_only)} JSON internal or privilege-style tags")
    lines.append(f"{len(comparison.manual_only)} manual-only extension names")
    lines.append(f"{len(comparison.manual_context_only)} manual umbrella, profile, or privileged names")

    lines.append("")
    lines.append("JSON-Only Extension Names")
    lines.extend(comparison.json_only or ["None"])

    lines.append("")
    lines.append("JSON Internal Or Privilege-Style Tags")
    lines.extend(comparison.json_internal_only or ["None"])

    lines.append("")
    lines.append("Manual-Only Extension Names")
    lines.extend(comparison.manual_only or ["None"])

    lines.append("")
    lines.append("Manual Umbrella, Profile, Or Privileged Names")
    lines.extend(comparison.manual_context_only or ["None"])

    lines.append("")
    lines.append("Cross Reference Notes")
    lines.append("Tier 2 compares normalized extension names from instr_dict.json against named extensions found in the ISA manual.")
    lines.append("JSON internal tags come from privilege or grouping names used by instr_dict rather than manual extension names.")
    lines.append("Manual umbrella or privileged names come from taxonomy, profiles, or privileged chapters and do not map one-to-one to instruction tags.")

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
