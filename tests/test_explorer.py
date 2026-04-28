from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import (  # noqa: E402
    build_shared_instruction_graph,
    find_multi_extension_instructions,
    group_by_extension,
    key_to_mnemonic,
    GraphEdge,
    MultiExtensionInstruction,
)
from manual import (  # noqa: E402
    collect_json_extensions,
    compare_extensions,
    extract_manual_tokens,
    normalize_json_tag,
    ExtensionComparison,
)
from report import (  # noqa: E402
    render_dot_graph,
    render_text_report,
)


class CoreTests(unittest.TestCase):
    def test_key_to_mnemonic(self) -> None:
        self.assertEqual(key_to_mnemonic("cbo_zero"), "CBO.ZERO")

    def test_group_by_extension(self) -> None:
        instr_dict = {
            "add": {"extension": ["rv_i"]},
            "sub": {"extension": ["rv_i", "rv_m"]},
        }
        grouped = group_by_extension(instr_dict)
        self.assertEqual(grouped["rv_i"], ["ADD", "SUB"])
        self.assertEqual(grouped["rv_m"], ["SUB"])

    def test_multi_extension_detection(self) -> None:
        instr_dict = {
            "add": {"extension": ["rv_i"]},
            "sub": {"extension": ["rv_i", "rv_m"]},
        }
        self.assertEqual(
            find_multi_extension_instructions(instr_dict),
            [MultiExtensionInstruction(mnemonic="SUB", tags=("rv_i", "rv_m"))],
        )

    def test_graph_builder(self) -> None:
        grouped = {
            "rv_a": ["LR.W", "SC.W"],
            "rv_b": ["SC.W", "XOR"],
            "rv_c": ["ADD"],
        }
        self.assertEqual(
            build_shared_instruction_graph(grouped),
            [GraphEdge(left="rv_a", right="rv_b", shared_count=1)],
        )


class ManualTests(unittest.TestCase):
    def test_normalize_json_tag(self) -> None:
        self.assertEqual(normalize_json_tag("rv_zba", "SH1ADD"), {"zba"})
        self.assertEqual(normalize_json_tag("rv_d_zfa", "FROUND"), {"d", "zfa"})
        self.assertEqual(normalize_json_tag("rv_svinval_h", "HINVAL.VVMA"), {"svinval", "h"})
        self.assertEqual(normalize_json_tag("rv_zicbo", "CBO.ZERO"), {"zicboz"})
        self.assertEqual(normalize_json_tag("rv_zicbo", "CBO.CLEAN"), {"zicbom"})

    def test_collect_json_extensions(self) -> None:
        instr_dict = {
            "add": {"extension": ["rv_i"]},
            "cbo_zero": {"extension": ["rv_zicbo"]},
            "hinval_vvma": {"extension": ["rv_svinval_h"]},
        }
        self.assertEqual(
            collect_json_extensions(instr_dict),
            {"rv32i", "zicboz", "svinval", "h"},
        )

    def test_extract_manual_tokens(self) -> None:
        text = """
        === "Smctr" Control Transfer Records Extension, Version 1.0
        == RV32I Base Integer Instruction Set, Version 2.1
        The A extension depends on ext:zicsr[].
        The corresponding supervisor-level extension, *Ssctr*, is similar.
        ==== ext:zicbom[] Extension for Cache-Block Management
        |*Svinval* |*1.0*
        """
        self.assertEqual(
            extract_manual_tokens(text),
            {"smctr", "ssctr", "rv32i", "a", "zicsr", "zicbom", "svinval"},
        )

    def test_compare_extensions(self) -> None:
        result = compare_extensions({"a", "s", "zba"}, {"a", "b", "zicsr"})
        self.assertEqual(result.matched, ("a",))
        self.assertEqual(result.json_only, ("zba",))
        self.assertEqual(result.json_internal_only, ("s",))
        self.assertEqual(result.manual_only, ("zicsr",))
        self.assertEqual(result.manual_context_only, ("b",))


class ReportTests(unittest.TestCase):
    def test_render_text_report(self) -> None:
        report = render_text_report(
            {"rv_i": ["ADD"]},
            [MultiExtensionInstruction(mnemonic="SUB", tags=("rv_i", "rv_m"))],
            ExtensionComparison(
                matched=("a",),
                json_only=("zba",),
                json_internal_only=("system",),
                manual_only=("zicsr",),
                manual_context_only=("b",),
            ),
            [GraphEdge(left="rv_a", right="rv_b", shared_count=2)],
        )
        self.assertIn("Tier 1 Summary", report)
        self.assertIn("rv_i | 1 instructions | e.g. ADD", report)
        self.assertIn("SUB | rv_i, rv_m", report)
        self.assertIn("1 direct matches", report)
        self.assertIn("1 JSON-only extension names", report)
        self.assertIn("1 JSON internal or privilege-style tags", report)
        self.assertIn("1 manual-only extension names", report)
        self.assertIn("1 manual umbrella, profile, or privileged names", report)
        self.assertIn("rv_a <-> rv_b (2 shared)", report)
        self.assertIn("Cross Reference Notes", report)

    def test_render_dot_graph(self) -> None:
        dot = render_dot_graph([GraphEdge(left="rv_a", right="rv_b", shared_count=2)])
        self.assertIn('graph riscv_extensions {', dot)
        self.assertIn('"rv_a" -- "rv_b" [label="2"];', dot)

    def test_end_to_end_small_fixture(self) -> None:
        instr_dict = {
            "add": {"extension": ["rv_i"]},
            "cbo_zero": {"extension": ["rv_zicbo"]},
            "sub": {"extension": ["rv_i", "rv_m"]},
        }
        grouped = group_by_extension(instr_dict)
        multi = find_multi_extension_instructions(instr_dict)
        json_extensions = collect_json_extensions(instr_dict)
        comparison = compare_extensions(json_extensions, {"rv32i", "m", "zicboz"})
        edges = build_shared_instruction_graph(grouped)
        report = render_text_report(grouped, multi, comparison, edges)

        self.assertIn("rv_i | 2 instructions | e.g. ADD", report)
        self.assertIn("SUB | rv_i, rv_m", report)
        self.assertIn("3 direct matches", report)
        self.assertIn("0 JSON-only extension names", report)


if __name__ == "__main__":
    unittest.main()
