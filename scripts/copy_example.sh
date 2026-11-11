#!/usr/bin/env bash
# Copiar desde Geant4 instalado; no realiza conexiones de red.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo/env/setup.sh"
prefix="$(spack location -i "$GEANT4_SPEC")"
args=(--prefix "$prefix")
if [[ -n "${1:-}" ]]; then args+=(--source "$1"); fi
if [[ -n "${2:-}" ]]; then args+=(--geometry "$2"); fi
python3 "$repo/scripts/local_example.py" copy "${args[@]}"
