# Style guide — reporting-agent

Binding for every `.tex` submodule this skill produces. Apply on every
draft and re-check on every editor pass.

## Voice and tense

- **Passive voice preferred** for describing methods, procedures, and
  observations: "The simulation was configured with…", "The results were
  compared against…", "A discrepancy was observed in…". This is a
  deliberate house rule for this skill, the opposite of
  `mastersThesis/docs/thesis_rules.md` §1.7 (which mandates active voice
  for the thesis). Do not mix the two conventions across projects.
- Never use first person ("we", "I", "our"). No exceptions.
- Past tense for what was actually done or observed in this run/process.
  Present tense is fine for general, time-invariant statements of fact or
  interpretation ("This behavior arises because…").
- No rhetorical questions, no contractions, no em dashes in prose (`---` or
  `—`). Use a comma, a colon, or split the sentence.
- Concise, precise sentences. State the actual finding; do not pad with
  hedging filler ("it can be observed that…", "it is worth noting that…").

## Acronyms and notation

- Spell out every acronym in full on first use, acronym in parentheses
  immediately after; use the short form thereafter.
- If the report reuses a symbol or notation across more than one
  submodule, define it once (a short nomenclature list or a LaTeX macro)
  and reference that definition rather than re-explaining it per file.

## Citations

- Only when the report references external sources. Default style: IEEE
  numeric (`[1]`, `[1, p. 5]`), consistent with
  `academic-reports`/`thesis-prose`. Use `biblatex`+`biber` (see
  `reference/latex_structure.md`); never hand-format a reference.
- No citation for the report's own results, data, or process — those are
  the subject of the report, not a foreign thought.
- Do not invent a source. If a claim needs support and no source is
  available, say so explicitly rather than fabricating a citation.

## Figures and tables — non-negotiable

- Every figure and every table is referenced in prose **before** it
  appears in the document (a forward `\cref{}`/`\ref{}` in the paragraph
  preceding the float).
- Every caption is a full descriptive sentence stating what is shown, not
  a bare label ("Trend of X" is not acceptable; "Cable tension against
  forward speed for the four sweep cases of Table 2" is).
- **Every figure and every table is immediately followed by a dedicated
  explanation paragraph.** The paragraph does not repeat the caption; it
  states what the reader should take from the float — the trend, the
  comparison, the anomaly, why it matters to the argument being built.
  A figure or table with no explanation paragraph after it is an
  incomplete submodule; the editor pass must catch and fix this before
  the report is considered done. `scripts/check_report.py` enforces this
  mechanically.
- Label every axis with quantity, symbol, and unit. Give every plotted
  series a legend when more than one series appears in one figure.
  Match scales across figures that are meant to be compared.

## Section-to-section reasoning ("storytelling")

- Every multi-part chapter opens with a short roadmap paragraph that
  previews its own subsections using forward `\cref{}` references — the
  reader should know, before reading subsection one, what each
  subsection will establish and why it is needed for the chapter's
  argument. See `03_Methodology.tex`'s opening paragraph in
  `mastersThesis` for the exact pattern being mirrored here (structure
  only; do not copy that document's active-voice wording).
- Every submodule closes, or the following submodule opens, with a
  bridging sentence that connects the two: what was just established and
  what it enables next. A submodule that begins with "Section 3 covers…"
  with no link back to what came before is a disconnected fragment, not a
  report.
- When dispatching a `reporting-writer` for one submodule, always include
  a one-line summary of the immediately preceding and following
  submodules so the writer can produce this bridging language without
  guessing at neighboring content it was never shown.

## What this skill does not do

- It does not generate figures from raw data on its own initiative. If
  the caller supplied raw data without plots, ask whether figures should
  be produced first (e.g., via the `scientific-visualization`/`matplotlib`
  skill) before drafting prose that references a figure that does not
  exist yet.
- It does not invent results. Every quantitative claim in the report
  traces to material the caller actually supplied.
