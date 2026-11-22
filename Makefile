# v2 targets are added per milestone (see REWORK.md §5).
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
# absolute interpreter path without resolving symlinks (a venv's python is a symlink)
PYABS := $(if $(filter /%,$(PY)),$(PY),$(if $(findstring /,$(PY)),$(CURDIR)/$(PY),$(shell command -v $(PY))))

.PHONY: verify-v1

# M0 test: the frozen v1 tree still verifies (needs souffle, pyshacl, rdflib).
verify-v1:
	@tmp=$$(mktemp -d) && git worktree add -q --detach "$$tmp/v1" v1 && \
	  { $(MAKE) -C "$$tmp/v1" verify PY="$(PYABS)"; s=$$?; git worktree remove --force "$$tmp/v1"; rmdir "$$tmp"; exit $$s; }
