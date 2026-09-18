---
name: reporting-agent
description: >-
  Use when the user hands over results (data, figures, metrics, logs) or
  describes a process and wants a structured, multi-file LaTeX academic
  report in English generated automatically. Produces one .tex file per
  section and one per subsection ("submodule"/"subsubmodule"), each
  submodule a working \input target from a main.tex. Academic clear
  English, passive voice preferred, mandatory captions, mandatory
  explanation paragraph after every figure and table, explicit
  reasoning/transitions between sections. Not for the mastersThesis
  project itself (that uses thesis-prose/academic-reports and the FSD
  active-voice house rule) — this skill is the general-purpose reporting
  tool for any other project's results.
license: MIT
---

# Reporting agent

Turns "here are results" or "here is a process" into a complete, compilable,
modular LaTeX report. Read the four reference files below before drafting
anything; they are binding, not optional background.

1. [reference/style_guide.md](reference/style_guide.md) — voice, tense,
   citations, captions, the mandatory explanation-paragraph rule, and the
   transition/storytelling rule. Read first; every subagent dispatch must
   carry these rules forward.
2. [reference/latex_structure.md](reference/latex_structure.md) — the
   submodule/subsubmodule file convention, naming, preamble, build command.
3. [reference/workflow.md](reference/workflow.md) — the six-phase
   orchestration procedure below, spelled out with the exact subagent briefs.
4. [reference/table_rules.md](reference/table_rules.md) — the one fixed
   way to build every table: skeleton, booktabs-only rule (mechanically
   enforced by the linter), and the two column patterns to choose
   between by table shape.

## Where output goes

This skill is a tool, not a project. Generated reports live **inside the
calling project**, not inside this skill's directory — typically
`<project>/reports/<topic>_<YYYY-MM-DD>/` (ask the user if the target
project or slot is ambiguous; never guess a destination outside the current
project without confirming). Never write report output under
`.opencode/skills/reporting-agent/`; that directory is the tool, not a
report instance. Copy `templates/report/` there as the starting skeleton.

## Workflow (see reference/workflow.md for the full brief text)

1. **Intake.** Read whatever results/process material the caller supplied.
   Identify the natural chapter decomposition (typically: introduction,
   process/methodology, results, discussion, conclusion — adapt to what was
   actually given; do not force a chapter that has nothing to say).
2. **Scaffold.** Copy `templates/report/` into the target report directory.
   Rename `sections/*.tex` to the real chapter/subsection names using the
   `NN_Name.tex` / `NN_MM_Name.tex` convention from
   [reference/latex_structure.md](reference/latex_structure.md). Wire
   `main.tex`'s `\input` list to the final chapter order.
3. **Dispatch writers.** For each independent chapter (and, within a
   multi-part chapter, each subsubmodule), fan out a `reporting-writer`
   subagent in parallel — this is genuine independent work, a legitimate
   `task`/`@reporting-writer` fan-out. Every dispatch brief MUST include: the
   assigned results/data slice, the chapter's role in the overall narrative,
   a one-line summary of the immediately preceding and following submodules
   (so the writer can open/close with a bridging sentence), and a pointer to
   `reference/style_guide.md`. See workflow.md for the exact brief template.
4. **Assemble.** Verify `main.tex`'s `\input` order matches the narrative
   logic decided in step 1; fix chapter-opening roadmap paragraphs (the
   `\cref{}`-forward-reference pattern from
   [reference/latex_structure.md](reference/latex_structure.md)) if the
   writers drafted them before the final ordering was fixed.
5. **Editor coherence pass.** Dispatch one `reporting-editor` subagent
   (sequential, after every writer has finished) over the whole assembled
   `sections/` tree: fix cross-chapter transitions, confirm every figure/
   table has a caption AND a following explanation paragraph, confirm every
   float is referenced in prose before it appears, confirm passive-voice/
   no-first-person compliance, confirm acronyms are spelled out on first
   use. Run `scripts/check_report.py <report-dir>` before and after the
   editor's pass; the editor fixes whatever the linter flags.
6. **Compile.** From the report directory, run
   `latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex`. Read the
   `.log` for undefined references/citations/warnings and fix them. A
   report is not done until it compiles clean and the linter passes.

## Subagents

- `reporting-writer` — drafts exactly one assigned `.tex` submodule.
  Registered at `.omp/agents/reporting-writer.md` (omp) and
  `.opencode/agents/reporting-writer.md` (opencode).
- `reporting-editor` — final coherence, caption, and style audit across the
  whole report; fixes what it finds. Registered at
  `.omp/agents/reporting-editor.md` (omp) and
  `.opencode/agents/reporting-editor.md` (opencode).

## House rule: passive voice is deliberate here

`300_Projects/mastersThesis/docs/thesis_rules.md` §1.7 mandates *active*
voice for the thesis. This skill deliberately does the opposite: **passive
voice preferred** for describing methods, procedures, and observations, per
explicit instruction. Do not import the thesis's active-voice rule into
output from this skill, and do not export this skill's passive-voice rule
into thesis work.
