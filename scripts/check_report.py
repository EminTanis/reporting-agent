#!/usr/bin/env python3
"""Deterministic linter for reporting-agent output.

Checks, per the mandatory rules in reference/style_guide.md:

1. Every float (\\begin{figure}/\\begin{table}) with a \\label is
   referenced (\\cref{}/\\Cref{}/\\ref{}) at an earlier position in true
   document reading order than the float itself. Reading order follows
   \\input{} recursively, starting from main.tex, so a roadmap chapter
   file's own forward \\cref (to a label that lives inside a nested
   subsubmodule it \\input()s) counts correctly.
2. Every float is immediately followed by a non-empty prose paragraph
   (not just whitespace, a comment, or another float/section command)
   before the next float or sectioning command, within the same file.
3. No first-person pronoun ("I ", "we ", "our ", case-insensitive word
   boundary) appears in running prose.

Usage:
    python check_report.py <report-dir>

Exits 0 with "OK" when there are zero hard failures, 1 otherwise. Prints
one diagnostic line per failure so an editor pass has something concrete
to act on.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\[Cc]?ref\{([^}]+)\}")
FLOAT_BEGIN_RE = re.compile(r"\\begin\{(figure|table)\}")
FLOAT_END_RE = re.compile(r"\\end\{(figure|table)\}")
TABLE_BEGIN_RE = re.compile(r"\\begin\{table\}")
TABLE_END_RE = re.compile(r"\\end\{table\}")
HLINE_RE = re.compile(r"\\hline\b")
CAPTION_COMMAND_RE = re.compile(r"\\caption\b")
TABULAR_ENV_RE = re.compile(r"\\begin\{(tabular\*?)\}")
LATEX_MARKUP_RE = re.compile(r"\\[a-zA-Z]+\*?|[{}$]")
SECTIONING_RE = re.compile(
    r"\\(chapter|section|subsection|subsubsection|input)\b"
)
FIRST_PERSON_RE = re.compile(r"\b([Ww]e|[Oo]ur|[Ii])\b")
COMMENT_LINE_RE = re.compile(r"^\s*%")


@dataclass
class Failure:
    kind: str
    file: str
    detail: str


@dataclass
class Doc:
    path: Path
    text: str
    lines: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.lines = self.text.splitlines()


def flatten_document(
    path: Path, report_dir: Path, visited: frozenset[Path] = frozenset()
) -> list[Doc]:
    """Recursively expand \\input{} directives depth-first, returning a
    flat list of Doc fragments in true document reading order. Each
    fragment holds one file's text between (or around) its own \\input
    calls, so a label defined inside a nested \\input target is preceded,
    in this flat list, by whatever text of the parent came before that
    \\input call — which is exactly what a forward \\cref in a chapter's
    roadmap paragraph needs to count against."""
    resolved = path.resolve()
    if resolved in visited:
        raise SystemExit(f"error: circular \\input detected at {path}")
    visited = visited | {resolved}

    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    fragments: list[Doc] = []
    pos = 0
    for m in INPUT_RE.finditer(text):
        target_rel = m.group(1)
        segment = text[pos : m.start()]
        if segment.strip():
            fragments.append(Doc(path=path, text=segment))
        pos = m.end()
        if target_rel == "preamble":
            continue
        target_path = report_dir / f"{target_rel}.tex"
        fragments.extend(flatten_document(target_path, report_dir, visited))
    tail = text[pos:]
    if tail.strip() or not fragments:
        fragments.append(Doc(path=path, text=tail if fragments else text))
    return fragments


def check_forward_references(docs: list[Doc]) -> list[Failure]:
    """A float's \\label must be \\ref'd/\\cref'd at an earlier offset in
    true document reading order than the float itself."""
    failures: list[Failure] = []
    seen_refs: set[str] = set()
    for doc in docs:
        text = doc.text
        events: list[tuple[int, str, str]] = []
        for m in REF_RE.finditer(text):
            for key in m.group(1).split(","):
                events.append((m.start(), "ref", key.strip()))
        for m in FLOAT_BEGIN_RE.finditer(text):
            end_match = FLOAT_END_RE.search(text, m.end())
            block_end = end_match.start() if end_match else len(text)
            label_match = LABEL_RE.search(text, m.end(), block_end)
            if not label_match:
                failures.append(
                    Failure(
                        "missing-label",
                        str(doc.path),
                        f"float at offset {m.start()} has no \\label",
                    )
                )
                continue
            events.append((m.start(), "float", label_match.group(1).strip()))
        events.sort(key=lambda e: e[0])

        for _, kind, payload in events:
            if kind == "ref":
                seen_refs.add(payload)
            else:
                if payload not in seen_refs:
                    failures.append(
                        Failure(
                            "no-forward-reference",
                            str(doc.path),
                            f"label '{payload}' is never \\ref'd/\\cref'd "
                            "before its float appears",
                        )
                    )
    return failures


def check_explanation_paragraphs(docs: list[Doc]) -> list[Failure]:
    """Every float must be followed by a non-empty prose paragraph before
    the next float or sectioning command, within the same fragment."""
    failures: list[Failure] = []
    for doc in docs:
        lines = doc.lines
        i = 0
        n = len(lines)
        while i < n:
            if FLOAT_END_RE.search(lines[i]):
                j = i + 1
                found_prose = False
                blocked = False
                while j < n:
                    line = lines[j]
                    stripped = line.strip()
                    if not stripped or COMMENT_LINE_RE.match(line):
                        j += 1
                        continue
                    if FLOAT_BEGIN_RE.search(line) or SECTIONING_RE.search(
                        line
                    ):
                        blocked = True
                        break
                    found_prose = True
                    break
                if not found_prose or blocked:
                    failures.append(
                        Failure(
                            "missing-explanation-paragraph",
                            str(doc.path),
                            f"float ending at line {i + 1} has no "
                            "explanation paragraph before the next "
                            "float/section",
                        )
                    )
                i = j
            else:
                i += 1
    return failures


def check_first_person(docs: list[Doc]) -> list[Failure]:
    failures: list[Failure] = []
    for doc in docs:
        for lineno, line in enumerate(doc.lines, start=1):
            if COMMENT_LINE_RE.match(line):
                continue
            m = FIRST_PERSON_RE.search(line)
            if m:
                failures.append(
                    Failure(
                        "first-person-pronoun",
                        str(doc.path),
                        f"line {lineno}: '{m.group(1)}' — "
                        f"{line.strip()[:80]}",
                    )
                )
    return failures


def _word_count(caption_text: str) -> int:
    """Approximate word count of a caption, stripping LaTeX commands and
    grouping/math delimiters so e.g. '\\si{\\kilogram}' or '$N$' count
    their remaining plain-text tokens rather than the markup itself."""
    stripped = LATEX_MARKUP_RE.sub(" ", caption_text)
    return len(stripped.split())


def _balanced_body(
    text: str, start: int, opening: str, closing: str
) -> tuple[int, str] | None:
    """Return the closing offset and body of a balanced LaTeX argument."""
    if start >= len(text) or text[start] != opening:
        return None

    depth = 1
    body_start = start + 1
    idx = body_start
    while idx < len(text):
        if text[idx] == "\\":
            idx += 2
            continue
        if text[idx] == opening:
            depth += 1
        elif text[idx] == closing:
            depth -= 1
            if depth == 0:
                return idx, text[body_start:idx]
        idx += 1
    return None


def find_braced_caption(text: str) -> tuple[int, str] | None:
    """Return a \\caption body after its optional short-caption argument."""
    match = CAPTION_COMMAND_RE.search(text)
    if not match:
        return None

    idx = match.end()
    while idx < len(text) and text[idx].isspace():
        idx += 1
    if idx < len(text) and text[idx] == "[":
        optional = _balanced_body(text, idx, "[", "]")
        if not optional:
            return None
        idx = optional[0] + 1
        while idx < len(text) and text[idx].isspace():
            idx += 1

    required = _balanced_body(text, idx, "{", "}")
    if not required:
        return None
    return match.start(), required[1]


def check_table_rules(docs: list[Doc]) -> list[Failure]:
    """Table markup follows reference/table_rules.md: mandatory captions,
    booktabs rules only (never \\hline), full-textwidth tabular* (never plain
    tabular), and captions of at most 8 words -- all inside any
    \\begin{table}...\\end{table} block."""
    failures: list[Failure] = []
    for doc in docs:
        text = doc.text
        for m in TABLE_BEGIN_RE.finditer(text):
            end_match = TABLE_END_RE.search(text, m.end())
            block_end = end_match.start() if end_match else len(text)
            block = text[m.end() : block_end]

            for hm in HLINE_RE.finditer(block):
                line_no = text[: m.end() + hm.start()].count("\n") + 1
                failures.append(
                    Failure(
                        "raw-hline-in-table",
                        str(doc.path),
                        f"line {line_no}: found \\hline inside a table; "
                        "use \\toprule/\\midrule/\\bottomrule (booktabs) "
                        "per reference/table_rules.md",
                    )
                )

            tabular_match = TABULAR_ENV_RE.search(block)
            if tabular_match and tabular_match.group(1) != "tabular*":
                line_no = (
                    text[: m.end() + tabular_match.start()].count("\n") + 1
                )
                failures.append(
                    Failure(
                        "plain-tabular-in-table",
                        str(doc.path),
                        f"line {line_no}: found \\begin{{tabular}} instead "
                        "of \\begin{tabular*}{\\textwidth}; every table "
                        "spans the full text width per "
                        "reference/table_rules.md",
                    )
                )

            caption = find_braced_caption(block)
            if not caption:
                line_no = text[: m.start()].count("\n") + 1
                failures.append(
                    Failure(
                        "missing-table-caption",
                        str(doc.path),
                        f"line {line_no}: table has no parseable \\caption; "
                        "every table requires a caption per "
                        "reference/table_rules.md",
                    )
                )
                continue

            caption_offset, caption_text = caption
            words = _word_count(caption_text)
            if words > 8:
                line_no = text[: m.end() + caption_offset].count("\n") + 1
                failures.append(
                    Failure(
                        "table-caption-too-long",
                        str(doc.path),
                        f"line {line_no}: caption is {words} words, "
                        "over the 8-word limit in "
                        "reference/table_rules.md",
                    )
                )
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <report-dir>", file=sys.stderr)
        return 2
    report_dir = Path(argv[1]).resolve()
    main_tex = report_dir / "main.tex"
    if not main_tex.is_file():
        print(f"error: {main_tex} not found", file=sys.stderr)
        return 2
    docs = flatten_document(main_tex, report_dir)
    if not docs:
        print(f"error: main.tex at {report_dir} produced no content")
        return 1

    failures: list[Failure] = []
    failures += check_forward_references(docs)
    failures += check_explanation_paragraphs(docs)
    failures += check_first_person(docs)
    failures += check_table_rules(docs)

    if not failures:
        print("OK: no hard failures")
        return 0

    for f in failures:
        rel = Path(f.file).name
        print(f"[{f.kind}] {rel}: {f.detail}")
    print(f"\n{len(failures)} hard failure(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
