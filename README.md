# reporting-agent

An [opencode](https://opencode.ai) skill (also usable with
[Oh My Pi](https://omp.sh) / `omp`) that turns given results or a process
description into a structured, multi-file LaTeX academic report in
English.

- One `.tex` file per section, one per subsection ("submodule" /
  "subsubmodule"), all `\input` from a single `main.tex`.
- Academic clear English, **passive voice preferred**, no first person.
- Every figure and every table is referenced in prose before it appears,
  and is followed by a mandatory explanation paragraph — a deterministic
  linter (`scripts/check_report.py`) enforces both.
- Two subagents (`reporting-writer`, `reporting-editor`) draft submodules
  in parallel and then unify voice, captions, and cross-section
  transitions so the result reads as one coherent report, not disjoint
  fragments.

Full workflow and style rules live in
[`.opencode/skills/reporting-agent/SKILL.md`](.opencode/skills/reporting-agent/SKILL.md)
and its `reference/` directory — read those once installed; this README
only covers getting it installed and invoked.

## Prerequisites

- [opencode](https://opencode.ai) and/or [omp](https://omp.sh).
- A LaTeX distribution with `latexmk` and `biber` on `PATH` (MiKTeX or
  TeX Live). The template uses `scrreprt` (KOMA-Script), `microtype`,
  `graphicx`, `booktabs`, `caption`/`subcaption`, `siunitx`, `amsmath`,
  `tikz`/`pgfplots`, `hyperref`+`cleveref`, `csquotes`, and
  `biblatex`+`biber` — all ship with a full MiKTeX/TeX Live install.
- Python 3.9+ on `PATH` to run the linter.

## Install

Pick one:

### Option A — installer script (recommended)

```sh
git clone https://github.com/EminTanis/reporting-agent.git
cd reporting-agent
./install.sh /path/to/your/project        # bash / macOS / Linux
# or, on Windows:
.\install.ps1 -Target C:\path\to\your\project
```

This merge-copies `.opencode/` and `.omp/` into the target project root
(defaults to the current directory if no target is given). It never
deletes anything in the target; it only adds or overwrites the
`reporting-agent` skill/agent files themselves.

### Option B — git submodule (for a monorepo/vault that tracks its tools)

```sh
git submodule add https://github.com/EminTanis/reporting-agent.git tools/reporting-agent
./tools/reporting-agent/install.sh .
```

This is exactly how the EminOS vault consumes its own copy: the
submodule is the source of truth, and the installer populates the live
`.opencode`/`.omp` directories at the vault root from it.

### Option C — manual

Copy these three paths from a clone into your project root, as-is:

```
.opencode/skills/reporting-agent/
.opencode/agents/reporting-writer.md
.opencode/agents/reporting-editor.md
.omp/agents/reporting-writer.md
.omp/agents/reporting-editor.md
```

## Use it

- **opencode**: the skill is auto-discovered from `.opencode/skills/`;
  mention a results file, a process, or a report request and opencode
  will pick it up by description, or invoke it explicitly.
- **omp**: same discovery, through omp's built-in `opencode` skill
  provider (reads `.opencode/skills/<name>/SKILL.md` from the project
  root by default) — no extra config needed. `skill://reporting-agent`
  resolves once installed.
- Either way, hand it the actual results/data/figures/process material
  and let it run its six-phase workflow (documented in
  `.opencode/skills/reporting-agent/reference/workflow.md`): intake,
  scaffold, parallel writer dispatch per submodule, assemble, editor
  coherence pass, compile.

## Package layout

```
reporting-agent/
  README.md, LICENSE, install.sh, install.ps1
  .opencode/
    skills/reporting-agent/
      SKILL.md
      reference/            style_guide.md, latex_structure.md, workflow.md
      templates/report/     working example: main.tex, preamble.tex,
                             sections/ (chapter + subsubmodule pattern,
                             a captioned table, a captioned tikz figure),
                             references.bib, .gitignore
      scripts/check_report.py
    agents/reporting-writer.md, reporting-editor.md
  .omp/
    agents/reporting-writer.md, reporting-editor.md
```

`.omp/agents/*.md` and `.opencode/agents/*.md` carry byte-identical
prompt bodies; only the frontmatter differs, because omp and opencode use
different (and mutually incompatible) subagent frontmatter contracts.

## License

MIT — see [`LICENSE`](LICENSE).
