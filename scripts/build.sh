#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo/env/setup.sh"
src="$repo/vendor/moleculardna"
build="$repo/build/molecular"
test -f "$src/CMakeLists.txt" || { echo 'Ejecutar primero bash scripts/copy_example.sh' >&2; exit 1; }
python3 "$repo/scripts/local_example.py" verify
test -s "$build/geometries/cube-centred-X-8.txt"
cd "$build"
# El CMake oficial comprueba geometries respecto al directorio de trabajo.
cmake -S "$src" -B "$build" -DWITH_GEANT4_UIVIS=OFF -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX"
cmake --build "$build" --parallel "${SLURM_CPUS_PER_TASK:-2}"
test -x "$build/molecular"
python3 "$repo/scripts/local_example.py" verify
cp "$repo/vendor/source.json" "$build/source.json"
echo 'Compilación terminada. Preparar la campaña smoke.json.'
