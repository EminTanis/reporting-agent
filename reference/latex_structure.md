# LaTeX structure — reporting-agent

The modular file convention this skill scaffolds and expects. Mirrors the
`\input`-per-submodule pattern used in
`300_Projects/mastersThesis/latex/Thesis.tex` and
`latex/sections/03_Methodology.tex`, generalized for arbitrary reports
(structure only; the passive-voice/no-first-person rules in
`style_guide.md` replace the thesis's active-voice rule).

## Directory layout

```
<report-dir>/
  main.tex              % documentclass, preamble \input, \input{sections/*}
  preamble.tex           % packages, float tuning, custom macros
  references.bib         % only if the report cites external sources
  .gitignore              % LaTeX build junk
  sections/
    01_Introduction.tex               % single-part chapter: content directly
    02_<ChapterName>.tex              % multi-part chapter: roadmap para + \input list
    02_01_<SubName>.tex               % subsubmodule, own file
    02_02_<SubName>.tex               % subsubmodule, own file
    03_<ChapterName>.tex              % next chapter, etc.
    0N_Conclusion.tex
  figures/
    <descriptive_name>.pdf            % vector where possible
```

## Naming convention

- Top-level chapter file: `NN_ChapterName.tex`, two-digit zero-padded
  order prefix, `ChapterName` in UpperCamelCase, no spaces.
- Subsubmodule file belonging to chapter `NN`: `NN_MM_SubName.tex`, same
  two-digit zero-padding for the subsection index `MM`.
- A chapter with only one part is just `NN_ChapterName.tex` with its
  content directly inside — do not create a pointless single-child
  subsubmodule file.
- A chapter with more than one part is a **thin roadmap file**: a
  `\chapter{}` (or `\section{}` in an `article`-class report), a short
  paragraph previewing each subsubmodule with forward `\cref{}`
  references (see `style_guide.md`), then an `\input{sections/NN_MM_...}`
  list in narrative order. Content lives in the subsubmodule files, not
  in the roadmap file.

## main.tex skeleton

```latex
\input{preamble}

\begin{document}

\maketitle
\tableofcontents
\listoffigures
\listoftables

\input{sections/01_Introduction}
\input{sections/02_<ChapterName>}
\input{sections/03_<ChapterName>}
\input{sections/0N_Conclusion}

\ifreportHasBibliography
  \printbibliography[heading=bibintoc]
\fi

\end{document}
```

The front matter order is fixed: title, table of contents, list of figures,
then list of tables. `tocbibind` places the two lists in the table of contents.
The bibliography follows the final content chapter and is added to the table of
contents by biblatex's `heading=bibintoc`; do not add a second manual
`\addcontentsline`. Omit the bibliography block only when the report has no
external citations and `references.bib` is empty.


Add or remove `\input` lines to match the final chapter order decided in
the intake/scaffold phase; the order in `main.tex` is the authoritative
narrative order and is what `scripts/check_report.py` uses to determine
"referenced before it appears."

## preamble.tex package set

Ship only packages proven to compile cleanly with the local MiKTeX/TeX
Live install (the thesis build already exercises the core set):

- `geometry` — page margins.
- `microtype` — tighter, more even justification.
- `graphicx` — figures.
- `booktabs` — table rules (`\toprule`/`\midrule`/`\bottomrule`, not raw
  `\hline\hline`).
- `caption`, `subcaption` — caption formatting, subfigures.
- `siunitx` — units in text and tables (`\SI{26.35}{\meter\per\second}`).
- `amsmath`, `amssymb` — math.
- `hyperref`, `cleveref` (load `hyperref` first, `cleveref` after) —
  clickable cross-references, `\cref{}`.
- `csquotes` — quotations if the report quotes a source.
- `tocbibind` with `notbib` — adds the lists of figures and tables to the
  table of contents without interfering with biblatex.
- `biblatex` with `backend=biber`, `style=ieee` — only if
  `references.bib` is non-empty; print it with `heading=bibintoc` so the
  bibliography itself appears once in the table of contents. Omit the
  bibliography packages entirely for a report with no external citations.
- `float` — the `[H]` specifier, used sparingly for a float that must sit
  exactly at its call-out.

Document class: `scrreprt` (KOMA-Script) by default — gives `\chapter`
through `\subsubsection`, which matches the chapter/submodule/subsubmodule
hierarchy this skill scaffolds. For a short single-chapter report, swap to
`scrartcl` and shift the hierarchy down one level (top-level submodules
become `\section` files, subsubmodules become `\subsection` files); the
one-file-per-submodule discipline stays identical either way.

## Build command

From the report directory:

```
latexmk -pdf -interaction=nonstopmode -synctex=1 main.tex
```

`latexmk` auto-detects `biber` when `biblatex` is loaded and
`references.bib` is non-empty — no separate biber invocation needed. Read
`main.log` after every build; an "undefined reference" or "undefined
citation" warning is a fix-it, not a pass.
