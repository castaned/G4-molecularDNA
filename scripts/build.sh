#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo/env/setup.sh" simulation
src="$repo/vendor/geant4/examples/advanced/dna/moleculardna"
build="$repo/build/molecular"
test -f "$src/CMakeLists.txt" || { echo 'Ejecutar primero bash scripts/fetch_example.sh' >&2; exit 1; }
test -s "$build/geometries/cube-centred-X-8.txt"
cd "$build"
# El CMake oficial comprueba geometries respecto al directorio de trabajo.
cmake -S "$src" -B "$build" -DWITH_GEANT4_UIVIS=OFF -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX"
cmake --build "$build" --parallel "${SLURM_CPUS_PER_TASK:-2}"
test -x "$build/molecular"
git -C "$repo/vendor/geant4" rev-parse HEAD > "$build/upstream-commit.txt"
echo 'Compilación terminada. Preparar la campaña smoke.json.'
