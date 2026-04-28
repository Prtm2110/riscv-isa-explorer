from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from core import key_to_mnemonic


MANUAL_REPO_URL = "https://github.com/riscv/riscv-isa-manual.git"
MANUAL_TOKEN_BLACKLIST = {
    "sh",
    "sm",
    "ss",
    "su",
    "sv",
    "machine",
    "state",
    "supervisor",
}

EXTENSION_REF_RE = re.compile(r"\bext(?:link)?:([A-Za-z0-9]+)(?:\[\])?")
BASE_RE = re.compile(r"\bRV(?:32|64|128)[IE]\b")
SINGLE_EXTENSION_RE = re.compile(r"\b([ABCDFHKMNPQSUV])\s+extension\b")
QUOTED_HEADING_RE = re.compile(r'^\s*=+\s+"([A-Za-z0-9]+)"', re.MULTILINE)
UNQUOTED_EXTENSION_HEADING_RE = re.compile(
    r"^\s*=+\s+([A-Za-z0-9]+)\b.*\bExtension\b",
    re.MULTILINE,
)
TABLE_EXTENSION_RE = re.compile(
    r"^\s*\|\s*[*`]?(RV(?:32|64|128)[IE]|[A-Z]|[A-Z][A-Za-z0-9]+)[*`]?\s*\|\s*[*`]?\d",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ExtensionComparison:
    matched: tuple[str, ...]
    json_only: tuple[str, ...]
    manual_only: tuple[str, ...]


def normalize_json_tag(tag: str, mnemonic: str) -> set[str]:
    if tag == "rv_i":
        return {"rv32i"}
    if tag == "rv64_i":
        return {"rv64i"}
    if tag == "rv128_i":
        return {"rv128i"}
    if tag == "rv_e":
        return {"rv32e"}
    if tag == "rv64_e":
        return {"rv64e"}
    if tag == "rv_zicbo":
        return {"zicboz"} if mnemonic == "CBO.ZERO" else {"zicbom"}

    body = re.sub(r"^rv(?:32|64|128)?_", "", tag.lower())
    if body == "svinval_h":
        return {"svinval", "h"}
    if body == tag.lower():
        return {body}
    return {part for part in body.split("_") if part}


def collect_json_extensions(instr_dict: dict[str, dict]) -> set[str]:
    found: set[str] = set()

    for key, entry in instr_dict.items():
        mnemonic = key_to_mnemonic(key)
        for tag in entry.get("extension", []):
            found.update(normalize_json_tag(tag, mnemonic))

    return found


def clone_or_update_manual(cache_dir: Path, refresh: bool = False) -> Path:
    if cache_dir.exists():
        if refresh:
            subprocess.run(
                ["git", "-C", str(cache_dir), "pull", "--ff-only"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        return cache_dir

    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", MANUAL_REPO_URL, str(cache_dir)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return cache_dir


def normalize_manual_token(token: str) -> str | None:
    cleaned = token.strip().lower()
    if cleaned in MANUAL_TOKEN_BLACKLIST:
        return None
    if cleaned in {"rv32i", "rv64i", "rv128i", "rv32e", "rv64e"}:
        return cleaned
    if len(cleaned) == 1 and cleaned in "abcdfhkmnpqsuv":
        return cleaned
    if re.fullmatch(r"(?:z|s|sm|ss|sv|sh)[a-z0-9]+", cleaned):
        return cleaned
    return None


def extract_manual_tokens(text: str) -> set[str]:
    tokens: set[str] = set()

    for pattern in (
        EXTENSION_REF_RE,
        BASE_RE,
        SINGLE_EXTENSION_RE,
        QUOTED_HEADING_RE,
        UNQUOTED_EXTENSION_HEADING_RE,
        TABLE_EXTENSION_RE,
    ):
        for match in pattern.findall(text):
            normalized = normalize_manual_token(match)
            if normalized:
                tokens.add(normalized)

    return tokens


def collect_manual_extensions(manual_dir: Path) -> set[str]:
    found: set[str] = set()

    for path in (manual_dir / "src").rglob("*.adoc"):
        found.update(extract_manual_tokens(path.read_text(encoding="utf-8")))

    return found


def compare_extensions(
    json_extensions: set[str],
    manual_extensions: set[str],
) -> ExtensionComparison:
    return ExtensionComparison(
        matched=tuple(sorted(json_extensions & manual_extensions)),
        json_only=tuple(sorted(json_extensions - manual_extensions)),
        manual_only=tuple(sorted(manual_extensions - json_extensions)),
    )
