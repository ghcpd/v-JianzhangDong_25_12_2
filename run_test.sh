#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -x "$VENV_DIR/bin/python" ]; then
  PY="$VENV_DIR/bin/python"
else
  PY="$PYTHON_BIN"
fi

# Run the automated test harness using the corrected requirements by default
"$PY" auto_test/auto_test.py --both
