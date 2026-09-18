# Table creation rule — reporting-agent

One fixed way to build every table, so every table in a report looks and
behaves the same regardless of which `reporting-writer` dispatch drafted
it. This is stricter than `style_guide.md`'s general caption/explanation
rule: this file fixes the actual LaTeX markup, not just the prose around
it. Table captions follow a different, shorter rule than the general
caption rule in `style_guide.md` (see below) — that difference is
deliberate and scoped to tables only; figure captions still follow
`style_guide.md`'s full-sentence rule unchanged.

## Fixed skeleton — always this shape

```latex
\begin{table}[!htb]
\centering
\caption{<Short label, at most 8 words>}
\label{tab:<snake_case_name>}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} <column spec>}
\toprule
<header row> \\
\midrule
<data rows> \\
\bottomrule
\end{tabular*}
\end{table}
```

Non-negotiable parts of this skeleton:

- `[!htb]` placement, always. `\centering`, always.
- **Every table spans the full text width.** Use `tabular*{\textwidth}`
  with `@{\extracolsep{\fill}}` as the first column-spec token — never
  plain `tabular`, and never a table left at its natural (narrower)
  content width. `\extracolsep{\fill}` distributes the extra width
  between columns; never manually widen a column with `p{Ncm}` guessing
  instead. `scripts/check_report.py` hard-fails on a `\begin{tabular}`
  found directly inside a `\begin{table}` block instead of
  `\begin{tabular*}{\textwidth}` — this is enforced, not just requested.
- **Caption is at most 8 words**, a short label rather than a sentence
  (e.g. `Measured pendulum periods`, not `Measured pendulum period and
  its square for the five pivot-to-bob-center lengths tested on the
  bench apparatus`). This is shorter than `style_guide.md`'s general
  "full descriptive sentence" caption rule, scoped to tables only.
  `scripts/check_report.py` hard-fails on a table caption over 8 words.
  Because the caption itself now carries very little, the mandatory
  explanation paragraph after the table (`style_guide.md`) is doing more
  of the descriptive work than it would after a long caption — do not
  shorten that paragraph to compensate for the short caption; if
  anything it needs to be more complete, since the caption no longer is.
- **The caption goes above the tabular**, before
  `\begin{tabular*}`. This is the opposite of a figure, where the
  caption goes below the content — captions sit above tables and below
  figures by convention; do not mix the two up.
- `\label{tab:...}` immediately after the caption, snake_case, always
  prefixed `tab:`. Never `Tab.`, `TAB_`, camelCase, or spaces.
- **Rules are `\toprule`/`\midrule`/`\bottomrule` from `booktabs`, never
  `\hline`.** `booktabs` is already loaded in `preamble.tex`.
  `scripts/check_report.py` hard-fails on any `\hline` found inside a
  `\begin{table}...\end{table}` block — this is enforced, not just
  requested.
- One `\midrule` between the header row and the data rows. Extra
  `\midrule`s inside the data rows are allowed, and encouraged, when the
  rows fall into natural logical groups (e.g. harmonics 1–4 vs. 5–8, or
  cases before/after a configuration change) — see the default style
  reference in Pattern B below. Never add a rule decoratively between
  literally every row; a rule must mark a real group boundary.

## Two fixed column patterns — pick by table shape, not by taste

A table is one of exactly two shapes. Identify which one it is, then use
that pattern's fixed column spec. Do not invent a third pattern. Both
patterns use the same `tabular*{\textwidth}{@{\extracolsep{\fill}} ...}`
wrapper from the skeleton above; only the interior column spec differs.

### Pattern A — parameter/value list (heterogeneous units per row)

Each row names a different quantity; the "value" column holds numbers in
different units from row to row (e.g. a configuration table: sample
interval in seconds, a dimensionless count, a duration in seconds). A
single column type cannot carry one unit for all of these rows, so
format each value with `\SI{}{}` or `\num{}` in the cell itself.

```latex
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} l l c@{}}
\toprule
Parameter & Description & Value \\
\midrule
$N$        & Number of cases evaluated & 4 \\
$\Delta t$ & Sample interval           & \SI{0.1}{\second} \\
$T$        & Total run duration        & \SI{60}{\second} \\
\bottomrule
\end{tabular*}
```

- Text columns: `l` (left-aligned). A short categorical/boolean column
  may be `c`.
- Value column: plain `c` (or `l`), formatted per cell with
  `\num{}`/`\SI{}{}` — never an `S` column here, because `S` columns
  assume one homogeneous unit down the whole column, which this shape
  does not have.
- See `templates/report/sections/02_01_FirstStage.tex` for a working,
  compiled example of this exact pattern.

### Pattern B — homogeneous data matrix (one quantity per column)

Each column is one quantity measured across several cases/samples/rows
(e.g. four sweep cases, each with a mass, a velocity, a tension). Every
value in a given column shares the same unit, so state the unit once in
the column header and let `siunitx`'s `S` column type decimal-align the
numbers automatically.

```latex
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} l S[table-format=2.1] S[table-format=3.1] S[table-format=1.2]@{}}
\toprule
{Case} & {Mass [\si{\kilogram}]} & {Velocity [\si{\meter\per\second}]} & {Tension [\si{\kilo\newton}]} \\
\midrule
1 & 12.3 & 26.4 & 1.05 \\
2 & 15.8 & 24.1 & 1.31 \\
3 & 18.2 & 21.9 & 1.58 \\
\bottomrule
\end{tabular*}
```

- First column (row labels/case numbers): `l` when it is a text label
  (a case name, a descriptive string). When it is itself a plain numeric
  index (a row number, a harmonic order, a sample index), type it `S`
  too, matching the default style reference below — do not force a
  numeric index into `l` just because it sits in the first column.
- Every homogeneous numeric column: `S[table-format=W.D]`, where `W.D`
  matches the widest value actually appearing in that column (integer
  digits `.` decimal digits). Get this right the first time; a mismatched
  `table-format` misaligns the whole column.
- Header cells over an `S` column are wrapped in `{}` (required by
  `siunitx` so it does not try to parse header text as a number). State
  the unit inside that header cell with `\si{}` when the quantity has a
  physical unit. When the quantity is symbolic/dimensionless (a Fourier
  index, a ratio, a phase given only as a bare math symbol), the header
  may be the math symbol itself instead of a unit — see the reference
  below, whose header row is entirely math-mode symbols.
- Data cells under an `S` column are bare numbers — no `\SI{}{}`, no
  units, no text. `siunitx` does the alignment; putting a unit in the
  cell breaks it.
- `S` columns inside `tabular*{\textwidth}{@{\extracolsep{\fill}} ...}`
  are verified compiling clean, with no overfull/underfull-hbox
  warnings: `\extracolsep{\fill}` stretches the inter-column gaps, and
  each `S` column still sizes and decimal-aligns itself independently
  from `table-format`, so the two mechanisms do not conflict.

#### Default style reference

The endorsed default look for a Pattern B table — all-numeric columns
typed `S` (including the index column), header cells as bare math-mode
symbols, and `\midrule` used to separate logical row groups rather than
the header only:

```latex
% Source - https://tex.stackexchange.com/a/112382
% Posted by Count Zero, modified by community. See post 'Timeline' for change history
% Retrieved 2026-09-18, License - CC BY-SA 4.0
\begin{tabular}{SSSSSSSS} \toprule
    {$m$} & {$\Re\{\underline{\mathfrak{X}}(m)\}$} & {$-\Im\{\underline{\mathfrak{X}}(m)\}$} & {$\mathfrak{X}(m)$} & {$\frac{\mathfrak{X}(m)}{23}$} & {$A_m$} & {$\varphi(m)\ /\ ^{\circ}$} & {$\varphi_m\ /\ ^{\circ}$} \\ \midrule
    1  & 16.128 & +8.872 & 16.128 & 1.402 & 1.373 & -146.6 & -137.6 \\
    2  & 3.442  & -2.509 & 3.442  & 0.299 & 0.343 & 133.2  & 152.4  \\
    3  & 1.826  & -0.363 & 1.826  & 0.159 & 0.119 & 168.5  & -161.1 \\
    4  & 0.993  & -0.429 & 0.993  & 0.086 & 0.08  & 25.6   & 90     \\ \midrule
    5  & 1.29   & +0.099 & 1.29   & 0.112 & 0.097 & -175.6 & -114.7 \\
    6  & 0.483  & -0.183 & 0.483  & 0.042 & 0.063 & 22.3   & 122.5  \\
    7  & 0.766  & -0.475 & 0.766  & 0.067 & 0.039 & 141.6  & -122   \\
    8  & 0.624  & +0.365 & 0.624  & 0.054 & 0.04  & -35.7  & 90     \\ \midrule
    9  & 0.641  & -0.466 & 0.641  & 0.056 & 0.045 & 133.3  & -106.3 \\
    10 & 0.45   & +0.421 & 0.45   & 0.039 & 0.034 & -69.4  & 110.9  \\
    11 & 0.598  & -0.597 & 0.598  & 0.052 & 0.025 & 92.3   & -109.3 \\ \bottomrule
\end{tabular}
```

Quoted here exactly as retrieved, for attribution — its own
`\begin{tabular}{SSSSSSSS}` is not wrapped in `tabular*{\textwidth}`. In
this project, wrap the same interior column spec and rows in the
skeleton above instead of quoting it bare:

```latex
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}} SSSSSSSS@{}}
```

Verified compiling against this project's actual `preamble.tex` as-is —
`amssymb` (already loaded) pulls in `amsfonts` for `\mathfrak`, no extra
package needed. Values in this reference are illustrative only; what
matters is the style (all-`S` typing, math-symbol headers, grouped
`\midrule`s), not these specific numbers.

Note the `table-format` deviation: this reference uses bare `S` with no
`table-format` on every column, not the `S[table-format=W.D]` the rule
above requires. That is deliberate here, not an exception to copy by
default: several of its columns mix signs and precisions row to row
(`+8.872`, `-146.6`, `90`) that do not share one `W.D` shape, so a single
`table-format` would misalign some rows. `siunitx` still aligns bare `S`
columns on the decimal point without it, just less tightly than a tuned
`table-format` would. **Default to specifying `table-format` per the
rule above** for a normal, uniform-precision column (e.g. the
mass/velocity/tension example earlier in this section); only drop it,
as here, when a column's own values genuinely do not share one format.

## Checklist before calling a table done

- [ ] Caption is at most 8 words, placed above the tabular.
- [ ] Table uses `tabular*{\textwidth}{@{\extracolsep{\fill}} ...}`, not
      plain `tabular`.
- [ ] Label is `tab:snake_case_name`.
- [ ] Rules are `\toprule`/`\midrule`/`\bottomrule`; no `\hline` anywhere.
- [ ] Shape identified as Pattern A or Pattern B; the matching column
      spec is used, not a hand-picked mix.
- [ ] Pattern B only: every `S` column's `table-format` matches the
      widest value in that column; header cells are `{}`-wrapped; no
      units inside data cells.
- [ ] The table is referenced in prose before it appears
      (`style_guide.md`), and followed by an explanation paragraph
      (`style_guide.md`) that carries the descriptive detail the short
      caption no longer does.
