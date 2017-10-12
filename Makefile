REQ_VER := 3.6
REQ_PY  := $(shell command -v python$(REQ_VER) 2>/dev/null)
REQUIREMENTS := requirements.txt

ENV_DIR      := env
ENV_BIN      := $(ENV_DIR)/bin
ENV_ACTIVATE := $(ENV_BIN)/activate
PY           := $(ENV_BIN)/python
PIP          := $(ENV_BIN)/pip

SRC_DIR  := scrapetools
TEST_DIR := test


init: $(ENV_ACTIVATE)
dev:
	make watch COMMAND=validate


$(ENV_ACTIVATE): $(REQUIREMENTS)
ifdef REQ_PY
	virtualenv -p $(REQ_PY) $(ENV_DIR)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(ENV_ACTIVATE)
else
	$(error Required python$(REQ_VER) to build)
endif


.PHONY: clean clean_hard lint typecheck test validate watch

clean:
	rm -rf build *.egg .mypy_cache cache
	find . | grep -E "__pycache__|\.pyc$$|\.pyo$$" | xargs rm -rf


clean_hard:
	rm -rf $(ENV_DIR)
	make clean


lint:
	@banner $@
	$(PY) -m flake8


typecheck:
	@banner $@
	$(PY) -m mypy $(SRC_DIR)

test:
	@banner $@
	$(PY) -m pytest

validate:
	make lint && \
	make typecheck && \
	make test

watch:
	while true; do \
		clear; \
		make $(COMMAND); \
		inotifywait -qre close_write $(SRC_DIR) $(TEST_DIR); \
	done
