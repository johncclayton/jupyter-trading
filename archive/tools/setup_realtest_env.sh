#!/usr/bin/env bash
set -euo pipefail

# Create a Python virtual environment named realtestextract and install tooling requirements.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$ROOT_DIR/realtestextract"
REQUIREMENTS_FILE="$ROOT_DIR/tools/requirements.txt"

if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo "Requirements file not found: $REQUIREMENTS_FILE" >&2
    exit 1
fi

python3 -m venv "$VENV_PATH"

source "$VENV_PATH/bin/activate"

pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

deactivate

echo "Virtual environment created at $VENV_PATH"
