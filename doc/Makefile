# --- Variables (Original Project Configuration) ---
SPHINXOPTS      ?=
SPHINXBUILD     ?= sphinx-build
SOURCEDIR       = source
BUILDDIR        = build
XMLDIR			= builxml
AUTOSUMMERYDIR  = $(SOURCEDIR)/devel/api
PYTHON          = python

# Color codes for terminal feedback
GREEN           = \033[0;32m
YELLOW          = \033[1;33m
BLUE            = \033[0;34m
NC              = \033[0m

# Explicit default goal
.DEFAULT_GOAL := help

.PHONY: help html htmlpure coverage clean api-json html-coverage-full epub check-sphinx

# Custom help menu reflecting your full workflow
help:
	@printf "$(BLUE)FTW Patch Build System$(NC)\n"
	@printf "Please use 'make <target>' where <target> is one of:\n\n"
	@printf "  $(GREEN)html$(NC)                Builds coverage AND dirhtml (Original Workflow)\n"
	@printf "  $(GREEN)htmlpure$(NC)            Builds standard HTML only\n"
	@printf "  $(GREEN)epub$(NC)                Builds ePub (with assets & custom_epub.css)\n"
	@printf "  $(BLUE)coverage$(NC)            Generates coverage reports\n"
	@printf "  $(BLUE)html-coverage-full$(NC)  Full run: Coverage + HTML + JSON Export\n"
	@printf "  $(YELLOW)clean$(NC)               Removes $(BUILDDIR) and API RSTs\n"

# Verify environment
check-sphinx:
	@command -v $(SPHINXBUILD) >/dev/null 2>&1 || { echo >&2 "Error: $(SPHINXBUILD) not found."; exit 1; }

# --- Original Workflows ---

# Your 'html' target: always cleans and runs coverage first
html: clean check-sphinx
	@printf "$(GREEN)%s$(NC)\n" "--- Running Coverage ---"
	@$(SPHINXBUILD) -M coverage "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@printf "$(GREEN)%s$(NC)\n" "--- Building HTML (dirhtml) ---"
	@$(SPHINXBUILD) -M dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

htmlpure: check-sphinx
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

coverage: check-sphinx
	@$(SPHINXBUILD) -M coverage "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html-debug:
	@$(SPHINXBUILD)  -T -b pseudoxml "$(SOURCEDIR)" "$(XMLDIR)" $(SPHINXOPTS) $(O)

html4test: clean check-sphinx
	@echo "INFO: Starting HTML Build..."  
	@$(SPHINXBUILD) -M dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "SUCCESS: HTML in $(BUILDDIR)/html"


html-coverage-full: check-sphinx
	@echo "INFO: Starting FULL COVERAGE check..."  
	@$(SPHINXBUILD) -b coverage "$(SOURCEDIR)" "$(BUILDDIR)/coverage"  
	@echo "INFO: Starting HTML Build..."  
	@$(SPHINXBUILD) -b dirhtml "$(SOURCEDIR)" "$(BUILDDIR)/html"  
	@echo "SUCCESS: Reports in $(BUILDDIR)/coverage, HTML in $(BUILDDIR)/html"

# --- New Asset-aware Targets ---

epub: check-sphinx
	@printf "$(YELLOW)%s$(NC)\n" "--- Building ePub output ---"
	@$(SPHINXBUILD) -M epub "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# --- Cleanup ---

clean:
	@printf "$(YELLOW)%s$(NC)\n" "--- Cleaning build directory and API cache ---"
	rm -rf $(BUILDDIR)
	@if [ -d "$(AUTOSUMMERYDIR)" ]; then \
		find "$(AUTOSUMMERYDIR)" -name "*.rst" -type f -delete 2>/dev/null || true; \
	fi
	@printf "$(GREEN)%s$(NC)\n" "Clean complete."

