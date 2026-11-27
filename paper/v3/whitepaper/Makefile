# WHITEPAPER.pdf from WHITEPAPER.md: the title and byline become pandoc metadata, the SVG charts are drawn again as
# PDF from the committed run records (figures.py, no API calls), and pandoc typesets the rest with LaTeX.
PY ?= $(if $(wildcard ../../../.venv/bin/python),../../../.venv/bin/python,python3)

WHITEPAPER.pdf: WHITEPAPER.md figures.py
	mkdir -p build/fig
	cd ../../.. && $(PY) paper/v3/whitepaper/figures.py --format pdf --out paper/v3/whitepaper/build/fig
	sed -e '1,3d' -e 's#(fig/\([a-z]*\)\.svg)#(build/fig/\1.pdf)#' WHITEPAPER.md > build/body.md
	pandoc build/body.md -f markdown-implicit_figures -o $@ --pdf-engine=xelatex \
	    -M title="$$(sed -n '1s/^# //p' WHITEPAPER.md)" -M author="Matthias Autrata" -M date="November 2026" \
	    -V geometry:margin=1in -V fontsize=11pt -V mainfont="Latin Modern Roman" -V monofont="Latin Modern Mono" \
	    -V colorlinks=true -V linkcolor=black -V urlcolor=blue

clean:
	rm -rf build
