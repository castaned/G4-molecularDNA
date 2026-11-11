---
layout: default
title: molecularDNA en YUCA
---

# molecularDNA en YUCA

Tutorial para reproducir el ejemplo **human_cell** de molecularDNA con
Geant4 11.3.0, desde el entorno C++ hasta una campaña Slurm y la inspección en ROOT.

La instalación de referencia es AlmaLinux 9, GCC 14.2.0 y CMake 3.31.5.
Los paquetes ya instalados se cargan con Spack; se compila únicamente
el ejemplo molecularDNA. No necesita instalar Geant4 ni privilegios de administrador.

## 1. Acceso y herramientas

Solicitar cuenta y método de acceso a YUCA. Conectarse usando el hostname autorizado
por los administradores; este tutorial no supone una dirección ni una partición.
Los comandos siguientes se ejecutan en **Bash dentro de YUCA**, no en PowerShell.

```bash
git clone https://github.com/castaned/G4-molecularDNA.git
cd G4-molecularDNA
git rev-parse HEAD
command -v git python3 sbatch srun
python3 --version
```

Se requiere Python 3.9 o posterior, sin paquetes Python adicionales. Si falta alguna
herramienta, consultar los módulos de YUCA. No instalar paquetes con sudo.

| Herramienta | Uso |
| --- | --- |
| GCC / g++ | Compilar las fuentes C++ de molecularDNA |
| CMake | Localizar Geant4 y generar la compilación |
| Geant4-DNA | Transporte microscópico, química y daño inicial al ADN |
| Slurm | Solicitar recursos y ejecutar trabajos en los nodos |
| Python | Preparar macros, semillas y campañas |
| ROOT | Leer árboles e histogramas y analizar resultados |

## 2. Cargar el entorno

```bash
source env/setup.sh
```

Este único comando configura **Spack, GCC 14.2.0, CMake 3.31.5, Geant4 11.3.0
y ROOT 6.24.08**, además de `CC` y `CXX`. CMake, Geant4 y GCC se cargan con
Spack; ROOT se carga con **`module load root/6.24.08`**, porque está instalado
como módulo de YUCA y no como paquete Spack. La configuración y la carga están en
el mismo archivo `env/setup.sh`; no hay que ejecutar los comandos internos aparte
ni usar otro archivo de configuración. El script muestra las versiones cargadas.

El compilador usado para construir CMake puede ser AOCC; la aplicación se compila
con GCC, como la instalación de Geant4 indicada. El spec `zen4` requiere nodos
compatibles: confirmar la partición o restricción apropiada con YUCA.

Solo si Spack encuentra varias coincidencias, consultar las instalaciones y elegir
el hash adecuado para el paquete que produce el error:

```bash
spack find -lv geant4
module avail root
# Sustituir HASH_REAL por el hash que corresponda a la instalación:
export GEANT4_SPEC='/HASH_REAL'
source env/setup.sh
```

Se pueden ajustar los valores predeterminados directamente en `env/setup.sh`;
las variables exportadas tienen prioridad. Si se utilizaba `config/yuca.local.sh`
en una versión anterior, trasladar sus specs personalizados al setup o a las
variables exportadas: ese archivo ya no se utiliza.

Se carga el entorno **una vez por sesión**. Repetir `source` en el mismo shell con
los mismos specs no vuelve a cargar los paquetes. Cada trabajo Slurm inicia otro
proceso y carga el mismo archivo para establecer su propio entorno; no requiere
ningún paso manual adicional. Usar una sesión limpia si
se habían cargado otras versiones. No se descargan bases de datos físicas durante
los trabajos: deben estar disponibles con la instalación Geant4 de YUCA.

## 3. Copiar molecularDNA desde la instalación de Geant4

```bash
bash scripts/copy_example.sh
```

El ejemplo ya está disponible con Geant4 en YUCA: **no hace falta descargar
molecularDNA de Internet**. El script consulta el prefijo de instalación mediante
`spack location -i`, busca el ejemplo en sus carpetas `examples` y lo copia a
`vendor/moleculardna`, dentro del repositorio del usuario. No modifica los archivos
compartidos de Geant4. Guarda su procedencia y sumas SHA-256 en `vendor/source.json`.

Si los ejemplos están en otra ubicación, indicar la ruta exacta:

```bash
spack location -i "$GEANT4_SPEC"
# Sustituir la ruta por la existente en YUCA:
bash scripts/copy_example.sh /ruta/Geant4/examples/advanced/dna/moleculardna
```

También se reconocen rutas antiguas `examples/extended/medical/dna/moleculardna`.
No se fija una ruta absoluta de YUCA sin haberla comprobado. Si no se encuentra
el ejemplo bajo el prefijo instalado, localizar la carpeta de fuentes/ejemplos
compartida y pasarla explícitamente.

Las geometrías son archivos de datos adicionales. Si la copia del ejemplo ya trae
`geometries/` o `geometries.tar.gz`, se reutilizan y copian/descomprimen localmente en
`build/molecular/geometries`. Si están en otra carpeta, pasar un segundo argumento:

```bash
bash scripts/copy_example.sh /ruta/moleculardna /ruta/geometries
# O usar un archivo de geometrías ya disponible localmente:
bash scripts/copy_example.sh /ruta/moleculardna /ruta/geometries.tar.gz
```

No es necesario tener las geometrías antes de copiar el ejemplo. Si todavía no
existen, el CMake oficial prepara `geometries/` durante la configuración.
Los cuatro archivos de `human_cell` se comprueban después de CMake.

En Geant4 11.3.0, CMake intenta descargar y descomprimir el dataset si no encuentra
las geometrías. Las fuentes de molecularDNA, en cambio, se copian de la instalación
local. Si el nodo no puede acceder al dataset, reutilizar `geometries/` de una
compilación funcional mediante el segundo argumento del script. La copia existente
nunca se sobrescribe silenciosamente.

Para migrar desde una versión previa de esta guía que usaba un checkout en
`vendor/geant4`, conservarlo como referencia; ya no se usa para nuevas compilaciones.
Si ya existe `build/molecular/geometries`, indicar esa misma carpeta como segundo
argumento, tras comprobar que corresponde a la geometría del ejemplo.
Si el CMake cache anterior apunta al checkout viejo, renombrar `build/molecular`
como respaldo y volver a preparar la copia/geometrías antes de compilar.

## 4. Compilar con Slurm

La cuenta de proyecto para este entorno de YUCA es **`p002`**. Los scripts Slurm
la incluyen como `#SBATCH --account=p002` y las campañas usan `"account": "p002"`.
Consultar primero las particiones y las políticas de esa cuenta:

```bash
sinfo
sbatch slurm/build.slurm
# Para indicar también la partición: sbatch --partition=PARTICION --account=p002 slurm/build.slurm
squeue -u "$USER"
```

El script solicita un nodo, una tarea y dos CPU; no utiliza MPI. Leer el archivo
`slurm-ID.out` al terminar y comprobar que existe `build/molecular/molecular`.
El ejemplo se configura con `WITH_GEANT4_UIVIS=OFF`: funciona sin escritorio gráfico.
Los recursos de compilación son valores iniciales que hay que ajustar si YUCA lo exige.

En una asignación interactiva autorizada también puede ejecutarse:

```bash
bash scripts/build.sh
```

No ejecutar simulaciones largas en el nodo de acceso.

## 5. Primera simulación: dos eventos

Antes de preparar, editar `config/smoke.json` si se requiere una partición.
La cuenta ya está fijada a `p002`; no dejarla vacía. La partición vacía usa el
valor predeterminado del sitio. Confirmar que esa
partición admite el entorno `zen4` de referencia.

```bash
python3 scripts/campaign.py prepare config/smoke.json runs/smoke-001
cat runs/smoke-001/task_00000/run.mac
python3 scripts/campaign.py submit runs/smoke-001 --dry-run
python3 scripts/campaign.py submit runs/smoke-001
squeue -u "$USER"
```

La prueba usa electrones de 0.662 MeV, dos eventos y un CPU. Es una comprobación
del flujo, no una muestra suficiente para estudiar rendimientos de daño.
La memoria de 8 GB y el tiempo de 30 minutos son valores de partida sin medir en YUCA;
la construcción de la geometría también consume memoria y tiempo con solo dos eventos.

La macro se deriva de `human_cell.mac`: conserva geometría, química, parámetros
de daño y distribución espacial. Añade semillas y sustituye partícula, energía,
eventos y nombre de salida. No contiene comandos de visualización.

## 6. Comprobar estado y salidas

```bash
# Sustituir ID por el número devuelto por sbatch.
sacct -j ID --format=JobID,State,ExitCode,Elapsed,MaxRSS
cat runs/smoke-001/logs/ID_0.err
cat runs/smoke-001/task_00000/finished.json
tail -n 40 runs/smoke-001/task_00000/simulation.log
find runs/smoke-001 -name '*.root'
```

`finished.json` debe indicar `success: true`, y Slurm debe terminar en `COMPLETED`
con código de salida cero. Un archivo ROOT existente por sí solo no demuestra
que todos los eventos se hayan procesado. Revisar también el final del log,
la ausencia de excepciones y el número de primarios al analizar los archivos.

Cada tarea tiene un directorio distinto. El ejecutable, plantilla, configuración,
semillas y sumas de integridad quedan registrados para reproducir la campaña.
Las geometrías se comparten mediante enlace y se comprueban antes de ejecutar.
No modificar ni borrar `build/molecular/geometries` mientras haya campañas pendientes.
Los archivos `started.json` impiden sobrescribir una tarea ya iniciada; para repetir
una prueba o recuperarse de un fallo, preparar una nueva carpeta de campaña.

## 7. Abrir los árboles con ROOT

ROOT ya está incluido en el entorno del paso 2; no hay que cargarlo de nuevo.
En una nueva sesión basta con el mismo `source env/setup.sh`.
El módulo confirmado en YUCA es `root/6.24.08`. Si cambia, ajustar `ROOT_MODULE`
en el setup o exportar esa variable antes de cargarlo. No usar `spack load root`.
Si un trabajo batch no conoce el comando `module`, el setup intenta inicializarlo
desde `MODULE_INIT` (por defecto `/etc/profile.d/modules.sh`); ajustar esa ruta
si la configuración de los nodos usa otra ubicación.
Escoger una instalación compatible con las bibliotecas C++ de la sesión.
Geant4 escribe el formato ROOT mediante su propio sistema de análisis; el paquete
ROOT se necesita aquí para leer y graficar los resultados, no para compilar el ejemplo.

Inspeccionar cada archivo generado, usando la ruta que devolvió `find`:

```bash
root -l -b -q 'analysis/inspect_output.C("runs/smoke-001/task_00000/molecular-dna.root")'
```

Si existen archivos de workers (`_t0`, `_t1`, etc.), inspeccionarlos también.
La macro comprueba los árboles `tuples/primary_source`, `chromosome_hits`,
`classification`, `source` y `damage`, y muestra sus filas. Una prueba pequeña
puede no generar lesiones: cero filas de daño no implica necesariamente un error.

Para explorar manualmente:

```bash
root -l runs/smoke-001/task_00000/molecular-dna.root
```

En ROOT:

```cpp
_file0->ls();
auto damage = (TTree*)_file0->Get("tuples/damage");
damage->Print();
damage->Scan("Event:TypeClassification:SourceClassification", "", "", 10);
```

Las filas de `damage` representan registros de daño, no primarios. Tampoco se deben
interpretar automáticamente las filas de `classification` como eventos independientes.
Para análisis de dosis y rendimiento usar las definiciones del ejemplo y conservar
el número de primarios y la normalización por réplica. El identificador Event puede
repetirse entre trabajos: identificar siempre campaña, tarea y evento.

### Graficar con las macros del ejemplo

El análisis utiliza adaptaciones de los scripts oficiales del mismo ejemplo:

| Partícula | Macro de graficación | Origen |
| --- | --- | --- |
| Electrones | `analysis/human_cell_electron.C` | `human_cell.C` |
| Alfas | `analysis/human_cell_alphas.C` | `human_cell_alphas.C` |
| Protones | `analysis/human_cell_proton.C` | `human_cell.C` |

```bash
# Si es una sesión nueva, cargar antes source env/setup.sh.
python3 scripts/plot_task.py runs/smoke-001 0
# Para una tarea alfa terminada:
python3 scripts/plot_task.py runs/alphas-001 0
```

El programa selecciona la macro según la partícula registrada y guarda PNG/PDF en
`task_00000/plots/`. Comprueba finalización y número de primarios, y fusiona los
archivos de workers únicamente dentro de esa tarea. No fusionar archivos de distintas
partículas, energías o réplicas. No graficar archivos parciales de trabajos con TIMEOUT.

Las macros conservan los cuatro paneles oficiales: especies, clases de daño,
SSB por origen y DSB por origen. Todas usan la masa de la geometría `human_cell`;
la macro alfa original tenía valores de HTB177 que se han adaptado. Verificar la
longitud de ADN del log; el valor predeterminado de 6405.886128 Mbp procede de
`human_cell.C` y se puede cambiar con `--dna-mbp`.

Las barras de error del ejemplo son exploratorias y deben contrastarse con réplicas.
La ejecución ROOT y la normalización numérica aún requieren validación en YUCA.
Consultar [adaptaciones y uso directo de las macros](https://github.com/castaned/G4-molecularDNA/blob/main/analysis/README.md).

## 8. Campañas configurables

Copiar `config/scan.json` y editar estos campos:

| Campo | Significado |
| --- | --- |
| `particles` | `e-`, `proton`, `alpha` |
| `energies` / `unit` | Energías cinéticas por partícula y unidad común |
| `events_per_job` | Primarios por tarea, no por hilo |
| `replicas` | Trabajos independientes por combinación |
| `seed_base` | Inicio de semillas; usar otro intervalo en campañas independientes |
| `physics_option` | Constructor Geant4-DNA: 2, 4 o 6 |
| `resources.cpus` | Hilos de un proceso molecularDNA por tarea |
| `resources.memory` | Memoria total por tarea/nodo único, por ejemplo `8G` |
| `resources.time` | Límite de tiempo por tarea |
| `resources.max_concurrent` | Máximo de tareas simultáneas del array |
| `resources.partition` / `account` | Valores reales de su asignación en YUCA |

`scan.json` contiene protones y alfas a 1, 5 y 10 MeV, con dos réplicas de diez
eventos: **12 tareas y 120 primarios** en total. Una energía de 5 MeV para un alfa
es energía total del ion, no 5 MeV por nucleón.

```bash
python3 scripts/campaign.py prepare config/scan.json runs/scan-001
python3 scripts/campaign.py submit runs/scan-001 --dry-run
python3 scripts/campaign.py submit runs/scan-001
```

El tamaño del array es partículas × energías × réplicas. Con dos CPU y dos trabajos
simultáneos se solicitan hasta cuatro CPU a la vez. No aumentar la concurrencia
sin revisar memoria, límites de Slurm y tiempo de la prueba inicial.

### Alfas y trabajos que exceden el tiempo

Se observó un trabajo de alfas terminado por `TIMEOUT` en YUCA. Por ello,
`config/alphas.json` y el barrido mixto `config/scan.json` solicitan ahora
**12 horas por tarea** (`"time": "12:00:00"`). Es un presupuesto inicial,
no una garantía de finalización: depende de energía, eventos, hilos y química.

```bash
python3 scripts/campaign.py prepare config/alphas.json runs/alphas-001
python3 scripts/campaign.py submit runs/alphas-001 --dry-run
python3 scripts/campaign.py submit runs/alphas-001
```

Usar una partición que admita 12 horas; comprobar su máximo antes de enviar:

```bash
sinfo -o '%P %l %a'
sacct -j ID --format=JobID,State,ExitCode,Elapsed,Timelimit,MaxRSS
```

Si el estado es `TIMEOUT`, Slurm agotó el tiempo de pared; no implica por sí mismo
un error de física ni falta de memoria. Revisar el log para identificar si terminó
la construcción de la geometría y cuántos eventos alcanzó. Aumentar el tiempo
en el JSON antes de preparar otra campaña, por ejemplo a `"24:00:00"` si la
partición lo permite, o reducir `events_per_job` y repartir primarios en más réplicas.
El tiempo de inicialización se paga de nuevo en cada tarea y debe considerarse.
No asumir que duplicar CPU reduce el tiempo a la mitad.

Para reintentar, conservar el directorio fallido y usar uno nuevo:

```bash
# Editar time y/o events_per_job en config/alphas.json primero.
python3 scripts/campaign.py prepare config/alphas.json runs/alphas-002
python3 scripts/campaign.py submit runs/alphas-002
```

La preparación guarda una copia de la configuración; editar el JSON original no
cambia el límite de una campaña ya preparada o enviada. No reutilizar salidas
ROOT de un TIMEOUT como si representaran el número de eventos solicitado.
Para ajustar recursos por partícula, preparar campañas separadas de electrones,
protones y alfas; el límite de un array se aplica a todas sus tareas.

La validación del JSON comprueba sintaxis y valores positivos; no certifica la
validez física de una energía. Consultar el intervalo de los modelos para la versión
y constructor elegidos. Para electrones, no extender este tutorial por encima de
1 MeV sin revisar y adaptar la física. El script limita las partículas al conjunto
inicial; otros iones requieren configuración GPS y revisión de modelos adicionales.

## 9. Problemas frecuentes

| Mensaje o síntoma | Acción |
| --- | --- |
| Spack encuentra varios paquetes | Ajustar el spec/hash en `env/setup.sh` o exportar la variable correspondiente |
| `Illegal instruction` | Verificar CPU del nodo y spec `zen4` con YUCA |
| Falta dataset Geant4 | Revisar instalación y variables de datos del entorno |
| No se encuentran fuentes o geometrías locales | Indicar sus rutas en `copy_example.sh`; no se usa descarga automática |
| `geometries/...` no encontrado | Ejecutar mediante el runner que crea el enlace |
| No existe `molecular` | Revisar salida del trabajo de compilación |
| `execve(): python3: No such file or directory` | El envío pasa ahora la ruta absoluta del intérprete y `srun --export=ALL`; actualizar scripts y preparar otra campaña. Si esa ruta no existe en los nodos, usar Python instalado en una ruta compartida |
| `TIMEOUT` o `OUT_OF_MEMORY` | Medir `sacct` y ajustar tiempo/memoria en una nueva campaña |
| `SLURM_MEM_PER_CPU, SLURM_MEM_PER_GPU, and SLURM_MEM_PER_NODE are mutually exclusive` | El runner limpia las variables CPU/GPU heredadas de Open OnDemand antes de `srun` y conserva la memoria por nodo de la campaña; actualizar el script y preparar una nueva campaña |
| `QOSMaxSubmitJobPerUserLimit` | Confirmar `--account=p002` y revisar los trabajos pendientes/en ejecución; la QOS limita el total enviado, no solo los simultáneos |
| Comando Geant4 desconocido | Revisar macro y confirmar versión 11.3.0 |
| ROOT falla al abrir | Comprobar archivo completo y compatibilidad de ROOT/libstdc++ |
| Tarea ya iniciada | Usar otra carpeta; no borrar la evidencia del intento |

## 10. Validación pendiente en el clúster

Si Slurm rechaza el envío por límite QOS, consultar:

```bash
squeue -u "$USER" -o '%.18i %.10a %.12q %.10T %.30R'
```

Reenviar con `sbatch --account=p002 slurm/build.slurm` si se había usado otra
cuenta. Si el límite persiste con `p002`, esperar a que terminen trabajos o
consultar la cuota con YUCA; no cancelar trabajos sin revisar cuáles son.
En arrays, reducir `%max_concurrent` limita la ejecución simultánea, pero no
necesariamente el número de tareas contabilizadas como enviadas por la QOS.

Este repositorio incluye pruebas del generador y del envío simulado. La primera
ejecución en YUCA debe confirmar los specs Spack, partición, datasets, compilación,
tiempo/memoria, eventos procesados y lectura ROOT. Registrar esos datos antes de
presentar los ejemplos como validados en el clúster.

[Fuentes y atribución](references.md) · [Publicar y mantener el repositorio](publishing.md)
