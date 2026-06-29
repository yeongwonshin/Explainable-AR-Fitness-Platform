#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$(dirname "$ROOT_DIR")"
zip -r explainable_ar_fitness_platform.zip "$(basename "$ROOT_DIR")" \
  -x "*/node_modules/*" "*/.venv/*" "*/__pycache__/*" "*.DS_Store"
