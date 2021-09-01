PYTHON = $(shell pyenv which python)
GREP := $(shell command -v ggrep || command -v grep)
SED := $(shell command -v gsed || command -v sed)

.PHONY: help
help:
	@awk '/^[^ \t]*:/ { gsub(":.*", ""); print }' Makefile

.PHONY: clean
clean: clean-build clean-pyc clean-test

.PHONY: clean-build
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr src/*.egg-info

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: lint
lint:
	flake8 nmfishingreport tests

.PHONY: test
test:
	py.test tests

.PHONY: test-all
test-all:
	tox

.PHONY: register
register: dist
	twine register dist/*.whl

.PHONY: release
release: dist
	twine upload dist/*

.venv:
	$(PYTHON) -m venv .venv
	./.venv/bin/pip install --upgrade pip

.PHONY: copy-db
copy-db: fishing_reports.db
	cp -i $< 20150918-$$(date +%Y%m%d)_fishing_reports.db

.PHONY: oxidize
oxidize:
	cd oxidize && pyoxidizer build --release
	find oxidize/build -path '*/release/*' -type f -perm -110 -exec cp {} . \; -quit

.PHONY: update-reqs
update-reqs: requirements.txt
		@$(GREP) --invert-match --no-filename '^#' requirements*.txt | \
				$(SED) 's|==.*$$||g' | \
				xargs ./.venv/bin/python -m pip install --upgrade; \
		for reqfile in requirements*.txt; do \
				echo "Updating $${reqfile}..."; \
				./.venv/bin/python -c 'print("\n{:#^80}".format("  Updated reqs below  "))' >> "$${reqfile}"; \
				for lib in $$(./.venv/bin/pip freeze --all --isolated --quiet | $(GREP) '=='); do \
						if $(GREP) "^$${lib%%=*}==" "$${reqfile}" >/dev/null; then \
								echo "$${lib}" >> "$${reqfile}"; \
						fi; \
				done; \
		done;
