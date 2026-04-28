from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


INSTR_DICT_DEFAULT = (
    Path(__file__).resolve().parent
    / "data"
    / "instr_dict.json"
)


@dataclass(frozen=True)
class MultiExtensionInstruction:
    mnemonic: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class GraphEdge:
    left: str
    right: str
    shared_count: int


def load_instr_dict(path: Path) -> dict[str, dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def key_to_mnemonic(key: str) -> str:
    return key.upper().replace("_", ".")


def group_by_extension(instr_dict: dict[str, dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)

    for key, entry in instr_dict.items():
        mnemonic = key_to_mnemonic(key)
        for tag in entry.get("extension", []):
            grouped[tag].append(mnemonic)

    return {tag: sorted(mnemonics) for tag, mnemonics in grouped.items()}


def find_multi_extension_instructions(
    instr_dict: dict[str, dict],
) -> list[MultiExtensionInstruction]:
    rows: list[MultiExtensionInstruction] = []

    for key, entry in instr_dict.items():
        tags = tuple(sorted(entry.get("extension", [])))
        if len(tags) > 1:
            rows.append(MultiExtensionInstruction(mnemonic=key_to_mnemonic(key), tags=tags))

    return sorted(rows, key=lambda item: item.mnemonic)


def build_shared_instruction_graph(grouped: dict[str, list[str]]) -> list[GraphEdge]:
    instruction_sets = {tag: set(values) for tag, values in grouped.items()}
    edges: list[GraphEdge] = []

    for left, right in combinations(sorted(instruction_sets), 2):
        shared = instruction_sets[left] & instruction_sets[right]
        if shared:
            edges.append(GraphEdge(left=left, right=right, shared_count=len(shared)))

    return sorted(edges, key=lambda item: (-item.shared_count, item.left, item.right))
