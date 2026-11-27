# v3 papers: the warrant dimension

Two documents, one evidence base.

| Document | Reader | Form | Claim |
| --- | --- | --- | --- |
| [`whitepaper/`](whitepaper/WHITEPAPER.md) | data and AI leaders, architects | Markdown, ~3,000 words, three charts (`figures.py`) | Context graphs and layers name exceptions and policy but leave them to precedent or to the model; the warrant dimension must be computed. |
| [`companion/`](companion/main.tex) | technical reviewers | LaTeX, full references | RQ1: representation is secondary (v1, v2). RQ2: warrants computed by an engine beat warrants read from text (v2, v3). |

Every number in either document comes from `spikes/v3/RESULTS.md` (v3), `paper/v2/PAPER.md` (v2) or
`paper/v1/PAPER.md` (v1), and each RESULTS table reproduces from the committed results with `bench/score.py`,
without API calls. The white paper's charts and counts come from the same records through `whitepaper/figures.py`.

## Build

    make -C paper/v3/companion          # latexmk; PDF in companion/build/

## Review

    .venv/bin/python paper/v3/review/review.py DRAFT --role reviewer --budget 1
    .venv/bin/python paper/v3/review/review.py DRAFT --role copyedit --models openai@gpt-6.2-sol --budget 0.5
    .venv/bin/python paper/v3/review/review.py DRAFT --role reader --models z-ai/glm-5.3-prime --persona "..." --budget 0.3

Figures: `.venv/bin/python paper/v3/whitepaper/figures.py` (SVG, text width; numbers in `fig/numbers.json`).

Prompts and the style sheet are in `review/`; output goes to `review/out/` (git-ignored). Reviews and copy-edits are
input to the next revision, not text to paste: each proposed edit is weighed, then applied or rejected.

## Before publishing

- No employer names ("a big US bank"), internal project names or results from outside this repository.
- Models named by id (gpt-6.2-sol: "a widely used frontier model"), never by where they ran.
- No absolute local paths; links to tags or `main`, not to branches.
- `git grep -nIiwE '<names to exclude>'` is empty for the paths that ship.
