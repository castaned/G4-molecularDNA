#!/usr/bin/env bash
# Configuración y carga de TODO el entorno YUCA en un único archivo.
# Uso: source env/setup.sh
# No cambiar opciones globales del shell interactivo.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo 'Usar: source env/setup.sh' >&2
  exit 2
fi
_g4_setup() {
  # Editar aquí los specs o hashes si cambia la instalación.
  # También se pueden definir estas variables antes de ejecutar source.
  export SPACK_SETUP="${SPACK_SETUP:-/shared/spack/share/spack/setup-env.sh}"
  export CMAKE_SPEC="${CMAKE_SPEC:-cmake@3.31.5%aocc@5.0.0 arch=linux-almalinux9-zen4}"
  export GEANT4_SPEC="${GEANT4_SPEC:-geant4@11.3.0%gcc@14.2.0}"
  export GCC_SPEC="${GCC_SPEC:-gcc@14.2.0}"
  # ROOT está publicado como módulo de YUCA, no como paquete Spack.
  export ROOT_MODULE="${ROOT_MODULE:-root/6.24.08}"
  export MODULE_INIT="${MODULE_INIT:-/etc/profile.d/modules.sh}"
  local signature="$SPACK_SETUP|$CMAKE_SPEC|$GEANT4_SPEC|$GCC_SPEC|$ROOT_MODULE|$MODULE_INIT"
  if [[ "${G4DNA_ENV_PID:-}" == "$BASHPID" && "${G4DNA_ENV_SIGNATURE:-}" == "$signature" ]]; then
    echo 'Entorno YUCA ya cargado en esta sesión.'
    return 0
  fi
  [[ -r "$SPACK_SETUP" ]] || { echo "No existe $SPACK_SETUP" >&2; return 1; }
  source "$SPACK_SETUP" || return
  spack load "$CMAKE_SPEC" || return
  spack load "$GEANT4_SPEC" || return
  spack load "$GCC_SPEC" || return
  # Los trabajos batch pueden necesitar inicializar Environment Modules.
  if ! type module >/dev/null 2>&1; then
    [[ -r "$MODULE_INIT" ]] || { echo 'No se encuentra module; indicar MODULE_INIT con la ruta de inicialización de módulos de YUCA.' >&2; return 1; }
    source "$MODULE_INIT" || return
  fi
  module load "$ROOT_MODULE" || return
  export CC="$(command -v gcc)" CXX="$(command -v g++)"
  [[ -n "$CC" && -n "$CXX" ]] || return 1
  echo 'Compilador C:'; "$CC" --version | head -n 1
  echo 'Compilador C++:'; "$CXX" --version | head -n 1
  echo 'Biblioteca C++:'; "$CXX" -print-file-name=libstdc++.so.6
  cmake --version | head -n 1
  if command -v geant4-config >/dev/null; then geant4-config --version; fi
  root-config --version || return
  export G4DNA_ENV_PID="$BASHPID" G4DNA_ENV_SIGNATURE="$signature"
}
_g4_setup
