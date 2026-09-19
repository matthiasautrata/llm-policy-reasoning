S1 = study1-interpretation
S2 = study2-scaling
PY ?= python3

.PHONY: verify score figures paper

verify:
	souffle -w -D - $(S1)/oracle/small/queries.dl > /dev/null
	souffle -w -D - $(S1)/oracle/large/queries.dl > /dev/null
	$(PY) $(S1)/oracle/check_ontology.py
	$(PY) $(S2)/verify.py $(S2)/worlds/*
	$(PY) $(S2)/check_shacl.py $(S2)/worlds/*

score:
	$(PY) $(S1)/harness/score.py $(S1)/results/original-20260831.jsonl
	$(PY) $(S1)/harness/score.py $(S1)/results/claude-subagents-20260918.jsonl
	$(PY) $(S2)/score.py $(S2)/results/scaling-pilot-20260918.jsonl

figures:
	$(PY) paper/figures.py

paper: figures
	$(PY) paper/build.py
