#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo/env/setup.sh"
src="$repo/build/visualization-source"
build="$repo/build/visualization"
geometry="$repo/build/molecular/geometries"
test -f "$src/CMakeLists.txt" || { echo 'Ejecutar python3 scripts/prepare_visualization.py' >&2; exit 1; }
test -s "$geometry/cube-centred-X-8.txt" || { echo 'Faltan las geometrías de la compilación normal' >&2; exit 1; }
mkdir -p "$build"
if [[ ! -e "$build/geometries" && ! -L "$build/geometries" ]]; then
  ln -s "$geometry" "$build/geometries"
fi
test -s "$build/geometries/cube-centred-X-8.txt" || { echo 'El enlace de geometrías no es válido' >&2; exit 1; }
cd "$build"
cmake -S "$src" -B "$build" -DWITH_GEANT4_UIVIS=ON -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX"
cmake --build "$build" --parallel "${SLURM_CPUS_PER_TASK:-1}"
cp "$src/single_segment.txt" "$build/single_segment.txt"
echo 'Visualización compilada. Desde el escritorio YUCA:'
echo "cd '$build'"
echo './molecular -t 1 -p 2'
