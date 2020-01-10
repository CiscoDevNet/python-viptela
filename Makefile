# Makefile
PYTHON_EXE = python3
TOPDIR = $(shell git rev-parse --show-toplevel)
VENV = venv_python_viptela
VENV_BIN=$(VENV)/bin
SRC_DIR = vmanage

help: ## Display help
	@awk -F ':|##' \
	'/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)

all: clean $(VENV) check test dist ## Setup python-viptela env and run tests

venv: ## Creates the needed virtual environment.
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV) $(ARGS)

$(VENV): $(VENV_BIN)/activate 

$(VENV_BIN)/activate: requirements.txt test-requirements.txt
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV)
	echo "export TOP_DIR=$(TOPDIR)" >> $(VENV_BIN)/activate
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt

deps: venv ## Installs the needed dependencies into the virtual environment.
	$(VENV_BIN)/pip install -r setup-requirements.txt
	$(VENV_BIN)/pip install -r requirements.txt -r test-requirements.txt

dev: deps ## Installs python-viptela in develop mode.
	$(VENV_BIN)/pip install -e ./

check-format: $(VENV)/bin/activate ## Check code format
	@( \
	set -eu pipefail ;\
	DIFF=`$(VENV)/bin/yapf -d -r *.py $(SRC_DIR)` ;\
	if [ -n "$$DIFF" ] ;\
	then \
	echo -e "\nFormatting changes requested:\n" ;\
	echo "$$DIFF" ;\
	echo -e "\nRun 'make format' to automatically make changes.\n" ;\
	exit 1 ;\
	fi ;\
	)

format: $(VENV_BIN)/activate ## Format code
	$(VENV_BIN)/yapf -i -r *.py $(SRC_DIR)

pycodestyle: $(VENV_BIN)/activate ## run pycodestyle
	$(VENV_BIN)/pycodestyle $(SRC_DIR)

pylint: $(VENV_BIN)/activate ## Run pylint
	$(VENV_BIN)/pylint --output-format=parseable --rcfile .pylintrc *.py $(SRC_DIR)

check: pycodestyle check-format pylint ## Check code format & lint

build: deps ## Builds EGG info and project documentation.
	$(VENV_BIN)/python setup.py egg_info

dist: build ## Creates the distribution.
	$(VENV_BIN)/python setup.py sdist --formats gztar


test: deps ## Run python-viptela tests
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt;tox -r

clean: ## Clean venv and binaries
	$(RM) -rf $(VENV)
	$(RM) -rf docs/build
	$(RM) -rf dist
	$(RM) -rf *.egg-info
	$(RM) -rf *.eggs
	find . -name "*.pyc" -exec $(RM) -rf {} \;

.PHONY: all clean $(VENV) test check format check-format pylint
