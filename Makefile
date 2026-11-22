# v2 targets are added per milestone (see REWORK.md §5).
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
# absolute interpreter path without resolving symlinks (a venv's python is a symlink)
PYABS := $(if $(filter /%,$(PY)),$(PY),$(if $(findstring /,$(PY)),$(CURDIR)/$(PY),$(shell command -v $(PY))))

.PHONY: verify verify-v1 worlds

# Regenerate every world (sizes S M L x seeds 1 2 3): base relations, L0 projections, questions, keys.
worlds:
	$(PY) world/gen.py

# M1 test: committed worlds are what the generator produces, and the independent Python reference
# reproduces every engine key (decided and open forks, all layers) in every world.
verify:
	$(PY) verify/check.py

# M0 test: the frozen v1 tree still verifies (needs souffle, pyshacl, rdflib).
verify-v1:
	@tmp=$$(mktemp -d) && git worktree add -q --detach "$$tmp/v1" v1 && \
	  { $(MAKE) -C "$$tmp/v1" verify PY="$(PYABS)"; s=$$?; git worktree remove --force "$$tmp/v1"; rmdir "$$tmp"; exit $$s; }
