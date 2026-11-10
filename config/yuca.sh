# Configuración de referencia para YUCA.
# Copiar a yuca.local.sh para cambiar especificaciones sin versionar rutas personales.
SPACK_SETUP=/shared/spack/share/spack/setup-env.sh
CMAKE_SPEC='cmake@3.31.5%aocc@5.0.0 arch=linux-almalinux9-zen4'
GEANT4_SPEC='geant4@11.3.0%gcc@14.2.0'
GCC_SPEC='gcc@14.2.0'
# ROOT se necesita para análisis, no para escribir ROOT con G4AnalysisManager.
# Consultar spack find -lv root y escribir un spec o hash no ambiguo.
ROOT_SPEC=''
