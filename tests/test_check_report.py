"""Regression tests for the reporting-agent report linter."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_report.py"
SPEC = importlib.util.spec_from_file_location("report_check", SCRIPT_PATH)
assert SPEC and SPEC.loader
report_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = report_check
SPEC.loader.exec_module(report_check)


class CaptionParsingTest(unittest.TestCase):
    def test_optional_nested_caption_counts_all_words(self) -> None:
        """A short-list argument cannot hide an overlong nested caption."""
        table = r"""\begin{table}
\caption[Measured values]{Measured values in \si{\kilogram} across five calibrated bench test cases}
\label{tab:sample}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} l@{}}
\toprule
Value \\
\bottomrule
\end{tabular*}
\end{table}
"""
        failures = report_check.check_table_rules(
            [report_check.Doc(path=Path("sample.tex"), text=table)]
        )

        self.assertEqual([failure.kind for failure in failures], ["table-caption-too-long"])

    def test_table_without_caption_fails(self) -> None:
        """A table cannot bypass the rule by omitting its caption."""
        table = r"""\begin{table}
\label{tab:sample}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} l@{}}
\toprule
Value \\
\bottomrule
\end{tabular*}
\end{table}
"""
        failures = report_check.check_table_rules(
            [report_check.Doc(path=Path("sample.tex"), text=table)]
        )

        self.assertEqual([failure.kind for failure in failures], ["missing-table-caption"])


if __name__ == "__main__":
    unittest.main()
