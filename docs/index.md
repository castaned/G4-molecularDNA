---
layout: default
title: molecularDNA en YUCA — guía práctica
---

# molecularDNA en YUCA

Del setup a una campaña Slurm y sus gráficas, usando **human_cell**.
Cada paso incluye una comprobación antes de continuar. Los comandos se ejecutan
en **Bash dentro de YUCA**, salvo los identificados como PowerShell de Windows.

> **Entorno comprobado en YUCA:** Geant4 11.3.0, GCC 14.2.0, CMake 3.31.5,
> Python 3.11.9 y ROOT 6.24/08; cuenta Slurm **p002**. El 11 de noviembre de 2026
> se completaron la compilación, una simulación de dos electrones y la lectura
> de sus árboles ROOT. También se generaron PNG/PDF con la macro de análisis.

**Recorrido:** [Repositorio](#repositorio) · [Entorno](#entorno) ·
[Geometrías](#geometrias) · [Compilación](#compilacion) · [Prueba](#prueba) ·
[Seguimiento](#seguimiento) · [Gráficas](#graficas) · [Mil eventos](#estadistica) ·
[Resultados](#resultados) · [Combinar](#combinar) · [Alfas](#alfas).

Si algo falla, consultar [solución de problemas](troubleshooting.md).

<a id="repositorio"></a>
## 1. Clonar o actualizar

Se necesita una cuenta de acceso a YUCA. Puede usarse la terminal del escritorio
Open OnDemand; las simulaciones se envían a Slurm.

Primera vez:

```bash
git clone https://github.com/castaned/G4-molecularDNA.git
cd G4-molecularDNA
```

Si la carpeta ya existe:

```bash
cd ~/G4-molecularDNA
git pull --ff-only
```

**Comprobación:** `pwd` debe apuntar al repositorio y `ls` debe mostrar
`env/`, `scripts/`, `config/` y `slurm/`. No clonar otra vez dentro de esa carpeta.

<a id="entorno"></a>
## 2. Un único setup

```bash
source env/setup.sh
```

Es el **único archivo de configuración y carga**. No hay que ejecutar sus comandos
internos aparte. Cada trabajo Slurm lo carga en su propio proceso; repetir `source`
en el mismo shell evita recargar los mismos paquetes.

| Componente | Carga en YUCA | Referencia |
| --- | --- | --- |
| C/C++ | Spack GCC | 14.2.0 |
| CMake | Spack | 3.31.5 |
| Geant4 | Spack | 11.3.0 |
| ROOT | `module load root/6.24.08` | 6.24/08 |
| Python | Instalación compartida de la sesión | 3.11.9 en la prueba |

**Comprobación:** el setup imprime las versiones sin errores. Verificar Python:

```bash
python3 --version
python3 -c 'import sys; print(sys.executable)'
```

Se requiere Python 3.9 o posterior. ROOT no está registrado como paquete Spack en
este entorno: **no usar `spack load root`**. Para cambios de instalación, editar
los specs o `ROOT_MODULE` en `env/setup.sh`. El spec de CMake usa `zen4`;
los nodos deben ser compatibles. Si el comando `module` no existe en batch,
ajustar `MODULE_INIT` a la ruta de inicialización de módulos del sitio.

<a id="geometrias"></a>
## 3. Copiar el ejemplo y preparar las geometrías

```bash
bash scripts/copy_example.sh
ls vendor/moleculardna/molecular.cc
ls vendor/moleculardna/human_cell.mac
```

El script copia molecularDNA desde la instalación local Geant4 a
`vendor/moleculardna`, sin descargar las fuentes ni modificar Geant4 compartido.
Registra ubicación y sumas SHA-256 en `vendor/source.json`.

Las geometrías son datos adicionales. Si están junto al ejemplo, se copian;
si faltan, **CMake prepara `build/molecular/geometries/` durante la configuración**.
En Geant4 11.3.0 puede intentar descargar y extraer un dataset de CERN.

> En la prueba de YUCA, esa descarga agotó los 500 segundos. Un archivo de 180 MB
> no era un tar.gz válido. Se reutilizó `geometries/` de otra compilación funcional;
> después la compilación terminó correctamente.

Si ya existe una carpeta completa de otra compilación:

```bash
mkdir -p build/molecular
# Sustituir la ruta. Copiar solo si el destino geometries aún no existe.
cp -a /ruta/compilacion-anterior/geometries build/molecular/
python3 scripts/local_example.py verify
```

Para preparar una copia nueva desde rutas explícitas:

```bash
bash scripts/copy_example.sh /ruta/moleculardna /ruta/geometries
```

**Comprobación:** se verifican los cuatro archivos requeridos por `human_cell`.
`ls -lh build/molecular/geometries/cube-centred-X-8.txt` debe mostrar el archivo.
Conservar `geometries/`: se reutiliza en recompilaciones y simulaciones; no se
descarga una vez por job. No modificarla con campañas activas.

<a id="compilacion"></a>
## 4. Compilar con Slurm

```bash
sbatch --account=p002 slurm/build.slurm
```

**Comprobación:** aparece `Submitted batch job ID_BUILD`. Sustituir `ID_BUILD`
por el número recibido:

```bash
squeue -j ID_BUILD
tail -n 30 slurm-ID_BUILD.out
sacct -j ID_BUILD --format=JobID,Account,State,ExitCode,Elapsed
ls -lh build/molecular/molecular
```

Esperar a que termine. Debe aparecer `COMPLETED`, código `0:0`, el ejecutable
y estas líneas al final del log:

```text
[100%] Built target molecular
Copia local y geometrías verificadas
Compilación terminada. Preparar la campaña smoke.json.
```

El build se configura sin interfaz gráfica. El trabajo de Open OnDemand que
también aparece en la cola es el escritorio, no la compilación: no cancelarlo.

<a id="prueba"></a>
## 5. Primera prueba: dos electrones

La prueba usa `human_cell`, electrones de 0.662 MeV, dos eventos, un CPU y 8 GB.

```bash
python3 scripts/campaign.py prepare config/smoke.json runs/smoke-001
python3 scripts/campaign.py submit runs/smoke-001 --dry-run
```

**Comprobación:** el comando debe incluir `--account=p002`, `--array=0-0%1`,
`--cpus-per-task=1`, `--mem=8G` y `--time=00:30:00`. También pasa la ruta absoluta
de Python, que debe estar disponible en los nodos de cómputo.

Enviar una sola vez:

```bash
python3 scripts/campaign.py submit runs/smoke-001
```

Anotar el número mostrado como `Enviada campaña: ID_SMOKE`. La preparación puede
tardar al comprobar archivos de geometría grandes. Para reintentar, preparar una
carpeta nueva, como `runs/smoke-002`, y conservar el intento anterior.

<a id="seguimiento"></a>
## 6. Seguir el trabajo y comprobar su finalización

Sustituir `ID_SMOKE` por el número real:

```bash
squeue -r -j ID_SMOKE
sacct -j ID_SMOKE --format=JobID,Account,State,ExitCode,Elapsed
cat runs/smoke-001/logs/ID_SMOKE_0.err
tail -n 30 runs/smoke-001/task_00000/simulation.log
```

| Señal | Significado | Acción |
| --- | --- | --- |
| `PD / PENDING` | Espera recursos o turno del array | Revisar motivo; no reenviar |
| `R / RUNNING` | Ejecutándose | Leer el log |
| `COMPLETED`, `0:0` | Slurm terminó sin error | Comprobar cierre y ROOT |
| `FAILED` | Error | Leer `.err`, `.out` y `simulation.log` |
| `TIMEOUT` | Agotó el tiempo solicitado | Revisar avance y preparar otro intento |
| No aparece en `squeue` | Salió de la cola | Consultar `sacct`; no asumir éxito |

`simulation.log` aparece al iniciar el ejecutable, después de las comprobaciones.
Un archivo ROOT puede existir antes de terminar: esperar al cierre correcto.

```bash
cat runs/smoke-001/task_00000/finished.json
```

**Comprobación:** `success: true`, `returncode: 0`, `ui_error: false`.

La prueba observada `2240070` (`runs/smoke-003`) terminó en **1 min 11 s**.
Ese tiempo corresponde a esa configuración y no predice el de otras partículas.

<a id="graficas"></a>
## 7. Leer ROOT y generar la primera gráfica

```bash
python3 scripts/plot_task.py runs/smoke-001 0
```

Se selecciona la macro según el manifest, se fusionan los workers de esa tarea
si hay varios, y se comprueba el número de primarios antes de graficar.

**Comprobación observada en la prueba de dos eventos:**

| Árbol | Filas |
| --- | --- |
| `tuples/primary_source` | 2 |
| `tuples/chromosome_hits` | 2 |
| `tuples/classification` | 2 |
| `tuples/source` | 2 |
| `tuples/damage` | 17 |

Los registros de `damage` no equivalen necesariamente a rupturas de cadena.
El número de primarios se obtiene de `primary_source`, no de `damage`.

| Partícula | Macro de análisis |
| --- | --- |
| Electrones | `analysis/human_cell_electron.C`, adaptada de `human_cell.C` |
| Protones | `analysis/human_cell_proton.C`, adaptada de `human_cell.C` |
| Alfas | `analysis/human_cell_alphas.C`, adaptada del script oficial de alfas |

**`human_cell.mac` configura la simulación; los archivos `.C` generan las gráficas.**
Los PNG/PDF se guardan en `task_00000/plots/`.

Las macros usan la masa de `human_cell` y una longitud de referencia de
6405.886128 Mbp. Confirmarla con el log de geometría; puede ajustarse con `--dna-mbp`.
No usar esa masa para HTB177 u otra geometría sin adaptarla.

Las figuras actuales muestran **valores centrales sin barras de error**.
`uncertainty: N/D` significa incertidumbre no determinada, no cero.
Se retiraron fórmulas heredadas que podían producir varianzas negativas.
SSB/DSB es no definido si DSB es cero. Las incertidumbres requieren un análisis
por evento o entre réplicas; más eventos no corrigen una fórmula incorrecta.

<a id="estadistica"></a>
## 8. Mil eventos: diez tareas con semillas independientes

**`config/electrons.json` ya está incluido en el repositorio.** No hace falta
crearlo copiando instrucciones del chat.

```bash
cat config/electrons.json
# Para modificarlo:
nano config/electrons.json
```

| Parámetro | Valor incluido | Efecto |
| --- | --- | --- |
| `particles` | `e-` | Electrones |
| `energies / unit` | `0.662 / MeV` | Una energía |
| `events_per_job` | 100 | Primarios por tarea, no por hilo |
| `replicas` | 10 | Diez ejecuciones |
| `seed_base` | 60001 | Semillas distintas |
| `resources.cpus` | 1 | Un hilo por tarea |
| `resources.memory` | `8G` | Memoria por tarea/nodo único |
| `resources.time` | `04:00:00` | Límite, no tiempo estimado |
| `resources.max_concurrent` | 2 | Hasta dos tareas simultáneas |
| `resources.account` | `p002` | Cuenta de proyecto |

Total: partículas × energías × réplicas × eventos por tarea =
**1 × 1 × 10 × 100 = 1,000 primarios**, si todas completan.

Las semillas de la tarea i son `seed_base + 2i` y `seed_base + 2i + 1`:
la tarea 0 usa 60001/60002 y la 9 usa 60019/60020. Usar intervalos que no se
superpongan entre campañas independientes.

```bash
python3 scripts/campaign.py prepare config/electrons.json runs/electrons-001 &&
python3 scripts/campaign.py submit runs/electrons-001 --dry-run
```

**Comprobación:** `--array=0-9%2` y `--account=p002`. Después:

```bash
python3 scripts/campaign.py submit runs/electrons-001
```

El manifest guarda la configuración al preparar. Editar el JSON original después
no cambia la campaña. Para otros eventos o semillas, usar otra carpeta,
por ejemplo `runs/electrons-002`.

### Leer el estado del array

```bash
squeue -r -j ID_ARRAY
sacct -j ID_ARRAY --format=JobID,State,ExitCode,Elapsed
```

`JobArrayTaskLimit` es normal con `%2`: mantiene hasta dos tareas ejecutándose.

{% assign array_image = site.static_files | where: "path", "/assets/images/slurm-array-status.png" | first %}
{% if array_image %}
![Estado real de la campaña 2240071 en YUCA]({{ '/assets/images/slurm-array-status.png' | relative_url }})
*Captura aportada durante la prueba. Es una instantánea de progreso, no evidencia
de que las diez tareas ya terminaron.*
{% endif %}

**Interpretación de la captura de la campaña 2240071:**

| Filas principales | Estado en esa captura | Interpretación |
| --- | --- | --- |
| `2240071_0` a `2240071_6` | `COMPLETED`, `0:0` | Siete tareas completas |
| `2240071_7` y `2240071_8` | `RUNNING` | Dos activas |
| `2240071_9` | `PENDING` | Espera turno |
| Filas con `.batch` o `.0` | Pasos internos | No son réplicas adicionales |

`Elapsed` es tiempo de pared. No contar los pasos internos como más trabajos
científicos. Antes de combinar, esperar a las diez tareas principales completas.

<a id="resultados"></a>
## 9. Encontrar resultados y gráficas

| Ruta dentro de `runs/electrons-001/` | Contenido |
| --- | --- |
| `manifest.json` | Configuración, semillas y procedencia |
| `submission.json` | ID y comando Slurm |
| `logs/` | Salidas `.out` y `.err` |
| `task_00000/` a `task_00009/` | Una carpeta por réplica |
| `task_00000/run.mac` | Parámetros y semillas exactas |
| `task_00000/simulation.log` | Registro de molecularDNA |
| `task_00000/finished.json` | Estado final e inventario ROOT |
| `task_00000/molecular-dna_t0.root` | Resultado del worker de esta configuración |
| `task_00000/plots/` | Gráficas, si se ejecutó `plot_task.py` |

```bash
find runs/electrons-001 -name '*.root'
head runs/electrons-001/task_00000/run.mac
python3 scripts/plot_task.py runs/electrons-001 0
```

Ese último comando grafica los **100 eventos de la tarea 0**, no los 1,000 combinados.
Desde el explorador del escritorio Open OnDemand se pueden abrir los PNG/PDF.

<a id="combinar"></a>
## 10. Combinar las réplicas y graficar

Combinar solo **la misma partícula, energía, geometría y configuración física**.
Conservar las réplicas para estimar su dispersión. Los números `Event` pueden
repetirse entre tareas: para análisis por evento hay que conservar también la
identidad de la tarea. Las macros adaptadas no mezclan fragmentos por ese identificador.

### A. Comprobar las diez finalizaciones

```bash
sacct -j ID_ARRAY --format=JobID,State,ExitCode,Elapsed
```

Todas las tareas principales deben estar `COMPLETED / 0:0`. Comprobar además:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path("runs/electrons-001")
manifest = json.loads((base / "manifest.json").read_text())
for task in manifest["tasks"]:
    folder = base / f'task_{task["id"]:05d}'
    status = json.loads((folder / "finished.json").read_text())
    if status.get("success") is not True:
        raise SystemExit(f"Tarea incompleta o fallida: {folder}")
    print(folder.name, "OK")
print("Todas las tareas tienen cierre correcto.")
PY
```

Si falta un archivo o aparece un error, no continuar con archivos parciales.

### B. Fusionar los archivos ROOT

La configuración incluida usa un CPU por tarea: esperamos diez archivos de worker t0.

```bash
find runs/electrons-001/task_* -name 'molecular-dna_t0.root'
hadd -f runs/electrons-001/electrons_1000.root \
  runs/electrons-001/task_*/molecular-dna_t0.root
```

`-f` reemplaza un combinado previo con ese nombre, sin modificar los originales.
Si cambia el número de CPU, revisar todos los workers en `finished.json`;
no aplicar el patrón de un único t0 a esa configuración.

### C. Verificar 1,000 primarios y generar PNG/PDF

```bash
root -l -b -q 'analysis/inspect_output.C("runs/electrons-001/electrons_1000.root",1000)' &&
root -l -b -q 'analysis/human_cell_electron.C("runs/electrons-001/electrons_1000.root","runs/electrons-001/plots_combined")'
```

**Comprobación:** `tuples/primary_source: 1000 filas`, sin errores.
Las figuras quedan en `runs/electrons-001/plots_combined/`.
Esta combinación aún debe comprobarse con la salida final de la campaña real;
la lectura y graficación de dos eventos sí fueron observadas.

<a id="alfas"></a>
## 11. Alfas y otras configuraciones

`config/alphas.json` contiene alfas a 1, 5 y 10 MeV, diez eventos por tarea y dos
réplicas: **6 tareas y 60 eventos**. La energía es total por ion, no por nucleón.
Solicita **12 horas por tarea** debido a un TIMEOUT reportado en una prueba previa.

```bash
sinfo -o '%P %l %a'
python3 scripts/campaign.py prepare config/alphas.json runs/alphas-001
python3 scripts/campaign.py submit runs/alphas-001 --dry-run
python3 scripts/campaign.py submit runs/alphas-001
```

Verificar que la partición admite ese tiempo. Doce horas son un presupuesto inicial,
no garantía de finalización. Revisar avance y memoria antes de aumentar tiempo
o repartir eventos. Cada tarea repite la inicialización; no extrapolar tiempos
de electrones directamente a alfas. Los límites de tiempo/memoria son por tarea.

`config/scan.json` mezcla partículas y energías: **no fusionar toda esa campaña
en un solo ROOT**. Agrupar únicamente condiciones idénticas. Comprobar que las
energías estén dentro del ámbito de los modelos físicos elegidos.

## 12. Lista final de comprobaciones

| Etapa | Condición para continuar |
| --- | --- |
| Setup | Versiones correctas, sin errores Spack/module |
| Copia | Fuentes y macro presentes |
| Geometría | Archivos verificados después de CMake |
| Build | `COMPLETED / 0:0` y ejecutable |
| Preparación | Manifest creado; eventos y semillas revisados |
| Envío | Cuenta p002, array y recursos correctos |
| Finalización | Tareas completas, `success: true` |
| ROOT | Primarios leídos iguales a los solicitados |
| Merge | Misma condición física y todos los workers pertinentes |
| Gráficas | PNG/PDF creados y normalización revisada |

[Solución de problemas](troubleshooting.md) · [Fuentes y atribución](references.md) ·
[Publicación y mantenimiento](publishing.md)
