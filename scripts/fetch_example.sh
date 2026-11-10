#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
commit=32390e802bd84a8b85ac02a90a3d31cf205dd5b7
dest="$repo/vendor/geant4"
mkdir -p "$repo/vendor" "$repo/build/molecular"
if [[ ! -d "$dest/.git" ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/Geant4/geant4.git "$dest"
  git -C "$dest" sparse-checkout init --cone
  git -C "$dest" sparse-checkout set examples/advanced/dna/moleculardna
  git -C "$dest" checkout --detach "$commit"
fi
[[ "$(git -C "$dest" rev-parse HEAD)" == "$commit" ]] || { echo 'El checkout no corresponde a Geant4 v11.3.0' >&2; exit 1; }
[[ -z "$(git -C "$dest" status --porcelain)" ]] || { echo 'Hay cambios en vendor/geant4; conservarlos aparte antes de continuar' >&2; exit 1; }
build="$repo/build/molecular"
if [[ ! -d "$build/geometries" ]]; then
  archive="$repo/vendor/geometries.tar.gz"
  if [[ ! -f "$archive" ]]; then
    curl --fail --location --retry 3 --output "$archive.part" \
      https://cern.ch/geant4-data/datasets/examples/advanced/dna/moleculardna/1/geometries.tar.gz
    mv "$archive.part" "$archive"
  fi
  # MD5 publicado en CMakeLists.txt de v11.3.0 (integridad del dataset).
  printf '%s  %s\n' 0bb690a782ce951b1a1973c6be2b1324 "$archive" | md5sum -c -
  tar -xzf "$archive" -C "$build"
fi
test -s "$build/geometries/cube-centred-X-8.txt"
echo "Fuentes y geometrías listas: $build"
