#!/usr/bin/env bash
# Uso: source env/setup.sh [simulation|analysis]
# No cambiar opciones globales del shell de la estudiante.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo 'Usar: source env/setup.sh [simulation|analysis]' >&2
  exit 2
fi
_g4_setup() {
  local mode="${1:-simulation}" repo config
  [[ "$mode" == simulation || "$mode" == analysis ]] || { echo 'Modo inválido' >&2; return 2; }
  repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || return
  config="$repo/config/yuca.sh"
  [[ ! -f "$repo/config/yuca.local.sh" ]] || config="$repo/config/yuca.local.sh"
  source "$config" || return
  [[ -r "$SPACK_SETUP" ]] || { echo "No existe $SPACK_SETUP" >&2; return 1; }
  source "$SPACK_SETUP" || return
  spack load "$CMAKE_SPEC" || return
  spack load "$GEANT4_SPEC" || return
  spack load "$GCC_SPEC" || return
  if [[ "$mode" == analysis ]]; then
    [[ -n "$ROOT_SPEC" ]] || { echo 'Configurar ROOT_SPEC en config/yuca.local.sh; consultar spack find -lv root' >&2; return 1; }
    spack load "$ROOT_SPEC" || return
  fi
  export CC="$(command -v gcc)" CXX="$(command -v g++)"
  [[ -n "$CC" && -n "$CXX" ]] || return 1
  echo 'Compilador C:'; "$CC" --version | head -n 1
  echo 'Compilador C++:'; "$CXX" --version | head -n 1
  echo 'Biblioteca C++:'; "$CXX" -print-file-name=libstdc++.so.6
  cmake --version | head -n 1
  if command -v geant4-config >/dev/null; then geant4-config --version; fi
  if [[ "$mode" == analysis ]]; then root-config --version || return; fi
}
_g4_setup "${1:-simulation}"
