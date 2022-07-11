.PHONY: help venv conda docker docstyle format style black test lint check coverage pypi
.DEFAULT_GOAL = help

PYTHON = python
PIP = pip
CONDA = conda
SHELL = bash

help:
	@printf "Usage:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[1;34mmake %-10s\033[0m%s\n", $$1, $$2}'

conda:  # Set up a conda environment for development.
	@printf "Creating conda environment...\n"
	${CONDA} create --yes --name etuples-env python=3.6
	( \
	${CONDA} activate etuples-env; \
	${PIP} install -U pip; \
	${PIP} install -r requirements.txt; \
	${PIP} install -r requirements-dev.txt; \
	${CONDA} deactivate; \
	)
	@printf "\n\nConda environment created! \033[1;34mRun \`conda activate etuples-env\` to activate it.\033[0m\n\n\n"

venv:  # Set up a Python virtual environment for development.
	@printf "Creating Python virtual environment...\n"
	rm -rf etuples-venv
	${PYTHON} -m venv etuples-venv
	( \
	source etuples-venv/bin/activate; \
	${PIP} install -U pip; \
	${PIP} install -r requirements.txt; \
	${PIP} install -r requirements-dev.txt; \
	deactivate; \
	)
	@printf "\n\nVirtual environment created! \033[1;34mRun \`source etuples-venv/bin/activate\` to activate it.\033[0m\n\n\n"

docker:  # Set up a Docker image for development.
	@printf "Creating Docker image...\n"
	${SHELL} ./scripts/container.sh --build

docstyle:
	@printf "Checking documentation with pydocstyle...\n"
	pydocstyle etuples/
	@printf "\033[1;34mPydocstyle passes!\033[0m\n\n"

format:
	@printf "Checking code style with black...\n"
	black --check etuples/
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

style:
	@printf "Checking code style with pylint...\n"
	pylint etuples/ tests/
	@printf "\033[1;34mPylint passes!\033[0m\n\n"

black:  # Format code in-place using black.
	black etuples/ tests/

test:  # Test code using pytest.
	pytest -v tests/ etuples/ --cov=etuples/ --cov-report=xml --html=testing-report.html --self-contained-html

coverage: test
	diff-cover coverage.xml --compare-branch=main --fail-under=100

pypi:
	${PYTHON} setup.py clean --all; \
	${PYTHON} setup.py rotate --match=.tar.gz,.whl,.egg,.zip --keep=0; \
	${PYTHON} setup.py sdist bdist_wheel; \
  twine upload --skip-existing dist/*;

lint: docstyle format style  # Lint code using pydocstyle, black and pylint.

check: lint test coverage  # Both lint and test code. Runs `make lint` followed by `make test`.
