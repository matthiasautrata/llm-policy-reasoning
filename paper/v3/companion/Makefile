# Figures and Table 4 come from the committed run records (no API calls); see paper/v3/whitepaper/figures.py.
ROOT := $(abspath ../../..)
PY ?= $(if $(wildcard $(ROOT)/.venv/bin/python),$(ROOT)/.venv/bin/python,python3)

build/main.pdf: main.tex refs.bib table-v3.tex fig/growth.pdf fig/cost.pdf
	latexmk -pdf -outdir=build main.tex

table-v3.tex fig/growth.pdf fig/cost.pdf: ../whitepaper/figures.py
	cd $(ROOT) && $(PY) paper/v3/whitepaper/figures.py --format pdf --out paper/v3/companion/fig \
	    --table paper/v3/companion/table-v3.tex --charts growth,cost

clean:
	latexmk -C -outdir=build main.tex
