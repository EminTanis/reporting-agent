# Workflow — reporting-agent

The six phases named in `SKILL.md`, expanded with the exact subagent
dispatch briefs.

## Phase 1 — Intake

Read every result/data/log/figure the caller supplied, or the process
description if no artifacts exist yet. Decide the chapter decomposition.
A typical shape:

```
01 Introduction              (context, what was done, why, report structure)
02 Process / Methodology     (often multi-part -> subsubmodules)
03 Results                   (often multi-part -> subsubmodules)
04 Discussion
05 Conclusion
```

Adapt freely — a report on a single experiment may not need a separate
Discussion chapter; a report on a multi-stage pipeline may need a
multi-part Process chapter with one subsubmodule per stage. Do not force
an empty chapter into existence.

## Phase 2 — Scaffold

Copy `templates/report/` into the target directory (see "Where output
goes" in `SKILL.md`). Rename `sections/*.tex` files to the real names
decided in Phase 1, following the `NN_Name.tex` / `NN_MM_Name.tex`
convention in `reference/latex_structure.md`. Update `main.tex`'s `\input`
list to match. Delete any template example chapter that has no
counterpart in the real report; do not leave placeholder chapters in the
final output.

## Phase 3 — Dispatch writers

Fan out one `reporting-writer` subagent per independent submodule (every
top-level single-part chapter, and every subsubmodule of a multi-part
chapter) in a single parallel batch — these are genuinely independent
drafting tasks. Do **not** dispatch the thin roadmap file itself to a
writer; write or fix that one directly once the writers finish (it needs
the final subsubmodule list, which does not exist until the writers are
back).

Each dispatch brief must contain, verbatim or adapted:

```
# Target
File: sections/<NN_or_NN_MM>_<Name>.tex
Role in report: <one sentence: what this submodule establishes>

# Material
<the actual results/data/figures/process text assigned to this submodule
— paste it or point at the exact file(s); never say "use the results",
name them>

# Neighbors (for bridging sentences — do not guess these)
Previous submodule: <one-line summary, or "none, this is the first">
Next submodule: <one-line summary, or "none, this is the last">

# Style
Follow .opencode/skills/reporting-agent/reference/style_guide.md exactly:
passive voice, no first person, every figure/table referenced before it
appears and followed by an explanation paragraph, acronyms spelled out on
first use, bridging sentences to the stated neighbors.

# Acceptance
The file compiles as a standalone \input target, contains at least one
bridging sentence connecting to each stated neighbor, and every float in
it has a caption plus a following explanation paragraph.
```

## Phase 4 — Assemble

Verify `main.tex`'s `\input` order is the true narrative order (it is the
order `scripts/check_report.py` uses for "referenced before it appears").
For every multi-part chapter, write or correct its roadmap paragraph now
that the final subsubmodule list and order are fixed — do this directly,
it is a short, tightly coupled edit, not a fan-out candidate.

## Phase 5 — Editor coherence pass

Run `python scripts/check_report.py <report-dir>` first; note every
finding. Dispatch one `reporting-editor` subagent (sequential, after every
writer is done — it needs the whole assembled tree) with:

```
# Target
Full sections/ tree at <report-dir>, main.tex for \input order.

# Task
Read every submodule in \input order. Fix, in place:
- any submodule opening/closing that does not bridge to its actual
  neighbor (compare against what the neighbor's file actually says, not
  the brief that was used to draft it — briefs can go stale)
- any float missing a caption, missing a following explanation
  paragraph, or referenced only after it appears
- any first-person pronoun or active-voice construction that should be
  passive per reference/style_guide.md
- any acronym used before its long form is given

# Input
Linter findings from scripts/check_report.py: <paste output>

# Acceptance
Re-running scripts/check_report.py after your edits reports zero hard
failures.
```

Re-run the linter after the editor finishes; loop once more only if hard
failures remain (do not loop indefinitely — a persistent failure after
one editor pass is escalated back to the orchestrating agent, not
silently retried).

## Phase 6 — Compile

```
cd <report-dir>
latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex
```

Read `main.log`. Fix any undefined reference, undefined citation, or
overfull-hbox-caused-by-content warning. The report is done only when it
compiles clean and the linter passes with zero hard failures.
