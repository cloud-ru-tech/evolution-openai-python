.PHONY: help install install-dev test lint format type-check clean build upload docs docs-clean docs-serve docs-pdf docs-epub docs-linkcheck docs-all docs-watch docs-open docs-watch-simple test-coverage release release-dry-run release-force bump-patch bump-minor bump-major bump-alpha bump-beta bump-rc

# Default target
help:
	@echo "Evolution OpenAI - Development Commands (Rye)"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package dependencies"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  shell        Activate virtual environment"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (ruff + type checking)"
	@echo "  lint-all     Run all linting checks (format + lint)"
	@echo "  lint-fix     Auto-fix linting issues where possible"
	@echo "  format       Format code (ruff)"
	@echo "  format-check Check code formatting"
	@echo "  type-check   Run type checking (pyright + mypy)"
	@echo ""
	@echo "Examples:"
	@echo "  run-examples      Run basic usage examples"
	@echo "  run-all-examples  Run all examples"
	@echo "  run-streaming     Run streaming examples"
	@echo "  run-async         Run async examples"
	@echo "  run-tokens        Run token management examples"
	@echo ""
	@echo "Build:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"
	@echo ""
	@echo "Documentation:"
	@echo "  docs            Build HTML documentation"
	@echo "  docs-clean      Clean documentation build"
	@echo "  docs-serve      Build and serve documentation locally"
	@echo "  docs-open       Open built documentation in browser"
	@echo "  docs-pdf        Build PDF documentation"
	@echo "  docs-epub       Build EPUB documentation"
	@echo "  docs-linkcheck  Check documentation links"
	@echo "  docs-all        Build all documentation formats"
	@echo "  docs-watch      Watch for documentation changes and rebuild"
	@echo "  docs-watch-simple  Simple file watching without auto-reload"

# Installation
install:
	rye sync

install-dev:
	rye sync --all-features

shell:
	@echo "Activating virtual environment..."
	@echo "Run: source .venv/bin/activate"
	@echo "Or use: rye run <command>"

# Testing
test:
	rye run pytest tests/ -v --cov=evolution_openai --cov-report=html --cov-report=term --cov-report=xml:coverage.xml --cov-report=json:coverage.json

# Code quality
lint:
	rye run ruff check .
	rye run pyright src/
	rye run mypy src/

lint-all: format-check lint
	@echo "All linting checks completed successfully!"

lint-fix:
	rye run lint:fix
	@echo "Linting issues fixed automatically!"

format:
	rye run format

format-check:
	rye run ruff format --check

type-check:
	rye run pyright src/
	rye run mypy src/

# Build and publish
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	rye build

upload: build
	rye publish --yes --token=$(PYPI_TOKEN)

upload-test: build
	rye publish --yes --repository testpypi --token=$(PYPI_TOKEN)

# Documentation
docs:
	@echo "Building HTML documentation..."
	rye run sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation built successfully!"
	@echo "Open: docs/_build/html/index.html"

docs-clean:
	@echo "Cleaning documentation build..."
	rm -rf docs/_build/
	@echo "Documentation build cleaned"

docs-serve: docs
	@echo "Starting documentation server..."
	@echo "Documentation will be available at: http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@cd docs/_build/html && rye run python -m http.server 8000

docs-open:
	@if [ -f "docs/_build/html/index.html" ]; then \
		echo "Opening documentation in browser..."; \
		open docs/_build/html/index.html || xdg-open docs/_build/html/index.html || echo "Please open docs/_build/html/index.html manually"; \
	else \
		echo "Documentation not built yet. Run 'make docs' first."; \
	fi

docs-pdf:
	@echo "Building PDF documentation..."
	@python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" || (echo "PDF generation not supported on Python 3.13+"; exit 1)
	rye run sphinx-build -b latex docs/ docs/_build/latex
	@cd docs/_build/latex && make
	@echo "PDF documentation built: docs/_build/latex/evolution-openai.pdf"

docs-epub:
	@echo "Building EPUB documentation..."
	@python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" || (echo "EPUB generation not supported on Python 3.13+"; exit 1)
	rye run sphinx-build -b epub docs/ docs/_build/epub
	@echo "EPUB documentation built: docs/_build/epub/evolution-openai.epub"

docs-linkcheck:
	@echo "Checking documentation links..."
	rye run sphinx-build -b linkcheck docs/ docs/_build/linkcheck
	@echo "Link check complete. See docs/_build/linkcheck/output.txt for results."

docs-all: docs-clean docs
	@echo "Building all supported documentation formats..."
	@python -c "import sys; print('Python version:', sys.version_info[:2])"
	@if python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)"; then \
		echo "Building PDF and EPUB (Python < 3.13)..."; \
		$(MAKE) docs-pdf docs-epub; \
		echo "All documentation formats built successfully!"; \
		echo "HTML: docs/_build/html/index.html"; \
		echo "PDF:  docs/_build/latex/evolution-openai.pdf"; \
		echo "EPUB: docs/_build/epub/evolution-openai.epub"; \
	else \
		echo "Only HTML documentation supported on Python 3.13+"; \
		echo "HTML documentation built: docs/_build/html/index.html"; \
	fi

docs-watch:
	@echo "Starting documentation auto-rebuild..."
	@echo "Documentation will be rebuilt every 3 seconds"
	@echo "View documentation at: docs/_build/html/index.html"
	@echo "Press Ctrl+C to stop"
	@echo ""
	@$(MAKE) docs >/dev/null 2>&1 && echo "$$(date '+%H:%M:%S') - Initial build completed"
	@while true; do \
		sleep 3; \
		$(MAKE) docs >/dev/null 2>&1 && echo "$$(date '+%H:%M:%S') - Documentation updated"; \
	done

docs-watch-simple:
	@echo "Starting simple documentation watcher..."
	@echo "Documentation will be rebuilt every 5 seconds"
	@echo "View at: docs/_build/html/index.html"
	@echo "Press Ctrl+C to stop"
	@while true; do \
		$(MAKE) docs >/dev/null 2>&1 && echo "$$(date '+%H:%M:%S') - Documentation rebuilt"; \
		sleep 5; \
	done

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "To activate the virtual environment, run: source .venv/bin/activate"

check: lint-all test

ci: check

# Examples
run-examples:
	@if [ -f .env ]; then echo "Загружение переменных окружения из файла .env..."; export $$(grep -v '^#' .env | xargs); fi; \
	rye run python examples/basic_usage.py

run-all-examples:
	@if [ -f .env ]; then echo "Загружение переменных окружения из файла .env..."; export $$(grep -v '^#' .env | xargs); fi; \
	rye run python examples/run_all_examples.py

run-streaming:
	@if [ -f .env ]; then echo "Загружение переменных окружения из файла .env..."; export $$(grep -v '^#' .env | xargs); fi; \
	rye run python examples/streaming_examples.py

run-async:
	@if [ -f .env ]; then echo "Загружение переменных окружения из файла .env..."; export $$(grep -v '^#' .env | xargs); fi; \
	rye run python examples/async_examples.py

run-tokens:
	@if [ -f .env ]; then echo "Загружение переменных окружения из файла .env..."; export $$(grep -v '^#' .env | xargs); fi; \
	rye run python examples/token_management.py

# Package info
info:
	@echo "Package: evolution-openai"
	@echo "Version: $$(rye version)"
	@echo "Python: $$(rye run python --version)"
	@echo "Rye: $$(rye --version)"

# Rye specific commands
update:
	rye sync

lock:
	rye lock

show:
	rye show

show-tree:
	rye show --tree

env-info:
	@echo "Virtual environment info:"
	@echo "Python executable: $$(rye run which python)"
	@echo "Virtual environment path: .venv"

# Virtual environment management
venv-create:
	rye sync

venv-remove:
	rm -rf .venv