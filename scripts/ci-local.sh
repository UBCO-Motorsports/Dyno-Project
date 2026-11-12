#!/usr/bin/env bash
# Runs the same steps as .github/workflows/tests.yml (one Python version).
# Usage: bash scripts/ci-local.sh
# On Windows without bash: use scripts/ci-local.ps1
set -euo pipefail
cd "$(dirname "$0")/.."

step=""
trap 'rc=$?; if [ $rc -ne 0 ]; then echo "FAILED step: $step" >&2; fi; exit $rc' EXIT

step="pip install -e .[dev]"
python -m pip install -e ".[dev]"

step="ruff check ."
python -m ruff check .

step="pytest -q"
python -m pytest -q

step="guardrails"
bash scripts/check_guardrails.sh

echo "ci-local: all steps passed"
