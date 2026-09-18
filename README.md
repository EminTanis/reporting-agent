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

Full workflow and style rules live in [`SKILL.md`](SKILL.md) and
[`reference/`](reference/) — read those once installed; this README only
covers getting it installed and invoked.

## Prerequisites

- [opencode](https://opencode.ai) and/or [omp](https://omp.sh).
- A LaTeX distribution with `latexmk` and `biber` on `PATH` (MiKTeX or
  TeX Live). The template uses `scrreprt` (KOMA-Script), `microtype`,
  `graphicx`, `booktabs`, `caption`/`subcaption`, `siunitx`, `amsmath`,
  `tikz`/`pgfplots`, `hyperref`+`cleveref`, `csquotes`, and
  `biblatex`+`biber` — all ship with a full MiKTeX/TeX Live install.
- Python 3.9+ on `PATH` to run the linter.

## Package layout

Everything is visible at the repo root — nothing is hidden inside a
dot-folder in this repository itself. `install.sh`/`install.ps1` are the
only things that know opencode/omp require the skill and its subagents
to end up under `.opencode/`/`.omp/` in the *target* project; that
placement happens at install time, not in this source tree.

```
reporting-agent/
  README.md, LICENSE, install.sh, install.ps1
  SKILL.md                skill entry point (frontmatter: name, description)
  reference/               style_guide.md, latex_structure.md, workflow.md
  templates/report/        working example: main.tex, preamble.tex,
                            sections/ (chapter + subsubmodule pattern, a
                            captioned table, a captioned tikz figure),
                            references.bib, .gitignore
  scripts/check_report.py  the caption/reference/voice linter
  agents/
    opencode/reporting-writer.md, reporting-editor.md
    omp/reporting-writer.md, reporting-editor.md
```

`agents/omp/*.md` and `agents/opencode/*.md` carry byte-identical prompt
bodies; only the frontmatter differs, because omp and opencode use
different (and mutually incompatible) subagent frontmatter contracts.

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

This places `SKILL.md` + `reference/` + `templates/` + `scripts/` at
`<target>/.opencode/skills/reporting-agent/`, and the agent files at
`<target>/.opencode/agents/` and `<target>/.omp/agents/`. It never
deletes anything else already in the target; it only adds or overwrites
the `reporting-agent` skill/agent files themselves.

### Option B — clone directly as the skill directory (opencode only)

opencode discovers `.opencode/skills/<name>/SKILL.md` directly, and this
repo's root already looks like a valid skill folder (`SKILL.md` +
`reference/` + `templates/` + `scripts/` right there), so you can clone
straight into place:

```sh
git clone https://github.com/EminTanis/reporting-agent.git .opencode/skills/reporting-agent
```

This skips the two subagents (`agents/opencode/*.md`,
`agents/omp/*.md` stay inside the cloned folder unused) — fine if you
only want the skill itself; run `install.sh`/`install.ps1` afterward if
you also want the subagents wired in.

### Option C — git submodule (for a monorepo/vault that tracks its tools)

```sh
git submodule add https://github.com/EminTanis/reporting-agent.git tools/reporting-agent
./tools/reporting-agent/install.sh .
```

This is exactly how the EminOS vault consumes its own copy: the
submodule is the source of truth, and the installer populates the live
`.opencode`/`.omp` directories at the vault root from it.

### Option D — manual

Copy `SKILL.md`, `reference/`, `templates/`, `scripts/` into
`<your-project>/.opencode/skills/reporting-agent/`, and the four files
under `agents/opencode/` and `agents/omp/` into
`<your-project>/.opencode/agents/` and `<your-project>/.omp/agents/`
respectively.

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
  `reference/workflow.md`, and inside the installed
  `.opencode/skills/reporting-agent/reference/workflow.md`): intake,
  scaffold, parallel writer dispatch per submodule, assemble, editor
  coherence pass, compile.

## License

MIT — see [`LICENSE`](LICENSE).
