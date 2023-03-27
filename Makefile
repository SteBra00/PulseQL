TOOL = PulseQL.py

all: check_python check_pip install_requirements test_tool

check_python:
	@command -v python3 >/dev/null || { echo "Python is not installed. Aborting."; exit 1; }
	@echo "Python: Ok"

check_pip: check_python
	@command python3 -m pip >/dev/null || { echo "Pip is not installed. Aborting."; exit 1; }
	@echo "Pip: Ok"

install_requirements: check_python check_pip
	@python3 -m pip install -q -r requirements.txt || { echo "Failed to install requirements. Aborting."; exit 1; }
	@echo "Requirements: Installed"

test_tool: check_python check_pip install_requirements
	@python3 $(TOOL) --version >/dev/null || { echo "Failed to open $(TOOL)"; return 1; }
	@echo "Final Test: Ok"
