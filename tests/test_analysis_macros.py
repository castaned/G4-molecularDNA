"""Comprobación estática de acumuladores de incertidumbre; no sustituye ROOT."""
from pathlib import Path
import re
import unittest


class AnalysisMacroTests(unittest.TestCase):
    def test_uncertainty_variables_are_declared_in_every_variant(self):
        folder = Path(__file__).resolve().parents[1] / "analysis"
        for particle in ("electron", "alphas", "proton"):
            with self.subTest(particle=particle):
                code = (folder / f"human_cell_{particle}.C").read_text(encoding="utf-8")
                code = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/', '', code)
                used = set(re.findall(r'\bSD_\w+\b', code))
                declarations = re.findall(r'\b(?:Float_t|Double_t)\s+([^;]+);', code)
                declared = {name for statement in declarations for name in re.findall(r'\bSD_\w+\b', statement)}
                self.assertTrue(used)
                self.assertEqual(used - declared, set(), "Variables SD utilizadas sin declarar")
