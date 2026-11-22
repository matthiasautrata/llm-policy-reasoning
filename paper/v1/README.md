# v1 paper: Rules in Context (September 2026)

Frozen copy of the v1 technical report: [`PAPER.md`](PAPER.md), [`whitepaper.pdf`](whitepaper.pdf) and its two figures.
Only the figure links in `PAPER.md` were changed, to point at this folder.

The studies, prompts, keys, transcripts, results and build scripts it cites live at git tag `v1`:

```
git checkout v1        # README.md there describes the layout
make verify            # needs Soufflé 2.4+, pyshacl, rdflib
```

From `main`, `make verify-v1` runs the same check in a temporary worktree.
