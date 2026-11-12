---
layout: default
title: Referencia técnica de molecularDNA
---

# Referencia técnica

[Volver a la receta](index.md)

Detalles opcionales para consultar después de reproducir los resultados.

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
sbatch --account=p067 slurm/build.slurm
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

**Comprobación:** el comando debe incluir `--account=p067`, `--array=0-0%1`,
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
| `resources.account` | `p067` | Cuenta de proyecto |

Total: partículas × energías × réplicas × eventos por tarea =
**1 × 1 × 10 × 100 = 1,000 primarios**, si todas completan.

Las semillas de la tarea i son `seed_base + 2i` y `seed_base + 2i + 1`:
la tarea 0 usa 60001/60002 y la 9 usa 60019/60020. Usar intervalos que no se
superpongan entre campañas independientes.

```bash
python3 scripts/campaign.py prepare config/electrons.json runs/electrons-001 &&
python3 scripts/campaign.py submit runs/electrons-001 --dry-run
```

**Comprobación:** `--array=0-9%2` y `--account=p067`. Después:

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
**Comprobado en YUCA el 11 de noviembre de 2026:** la campaña `2240071`
se combinó y el archivo resultante contiene los 1,000 primarios solicitados.
También se generaron los PNG/PDF. Ver [el registro de la prueba y sus resultados](validation.md).

En esa prueba, `classification` y `source` contienen 640 filas y `damage` contiene
2,852 registros. No todos los árboles tienen una fila por primario; la comprobación
de los 1,000 eventos corresponde a `primary_source`. No interpretar las 640 filas
como 640 primarios ni concluir a partir de ellas cuántos eventos no tuvieron daño.

<a id="alfas"></a>
## 11. Alfas: dos eventos por job y análisis separado por energía

Este recorrido reproduce **1, 5 y 10 MeV**, con **2 eventos por tarea y 10 réplicas
por energía**: 30 tareas, 20 primarios por energía y 60 en total. La energía es
cinética total del ion, no por nucleón. Todas usan la misma geometría human_cell.

### A. Crear una configuración de tareas cortas

Desde la raíz del repositorio, con el entorno cargado:

~~~bash
python3 - <<'PY'
import json
from pathlib import Path
cfg = json.loads(Path("config/alphas.json").read_text())
cfg.update(name="alphas-small", particles=["alpha"], energies=[1, 5, 10],
           unit="MeV", events_per_job=2, replicas=10, seed_base=80001)
cfg["resources"].update(cpus=1, memory="8G", time="12:00:00",
                        max_concurrent=2, account="p067")
Path("config/alphas-small.local.json").write_text(json.dumps(cfg, indent=2) + "\n")
PY
~~~

El archivo local queda separado del preset original. No modifica campañas ya
preparadas. Dos eventos por tarea reducen el trabajo de transporte/química de cada
job, pero cada uno repite la inicialización de la geometría.

Se solicita **1 CPU por tarea**, hasta **2 tareas simultáneas** y **12 horas por
tarea**. Confirmar que la partición admite ese límite; no es una garantía de
finalización. La concurrencia es distinta del número de réplicas.

~~~bash
sinfo -o '%P %l %a'
cat config/alphas-small.local.json
~~~

### B. Preparar y enviar 30 tareas

~~~bash
python3 scripts/campaign.py prepare config/alphas-small.local.json runs/alphas-small-001 &&
python3 scripts/campaign.py submit runs/alphas-small-001 --dry-run
~~~

**Comprobación:** el comando debe incluir --array=0-29%2, --account=p067,
--cpus-per-task=1 y --time=12:00:00. Después enviar una sola vez:

~~~bash
python3 scripts/campaign.py submit runs/alphas-small-001
~~~

Anotar el ID recibido. Enviar otra configuración exige otro directorio y un
intervalo de semillas independiente; no sobrescribir resultados previos.

### C. Identificar qué tarea corresponde a cada energía

campaign.py recorre partículas, energías y réplicas en ese orden. Para la
configuración de arriba, el reparto es:

| Energía | Carpetas | Tareas | Primarios al completar el grupo | Semillas del grupo |
| --- | --- | --- | --- | --- |
| 1 MeV | task_00000 a task_00009 | 10 | 20 | 80001 a 80020 |
| 5 MeV | task_00010 a task_00019 | 10 | 20 | 80021 a 80040 |
| 10 MeV | task_00020 a task_00029 | 10 | 20 | 80041 a 80060 |

Comprobar el reparto real guardado en el manifest:

~~~bash
python3 - <<'PY'
import json
from pathlib import Path
m = json.loads(Path("runs/alphas-small-001/manifest.json").read_text())
for t in m["tasks"]:
    print(f'task_{t["id"]:05d}', t["particle"], t["energy"], t["unit"],
          "replica", t["replica"], "seeds", t["seeds"])
PY
~~~

Si se modifica el orden de las energías o el número de réplicas, también cambia
el mapa de carpetas. No aplicar los patrones siguientes sin comprobar el manifest.

### D. Esperar al cierre correcto

Sustituir ID_ALPHA por el identificador recibido:

~~~bash
squeue -r -j ID_ALPHA
sacct -j ID_ALPHA --format=JobID,Account,State,ExitCode,Elapsed
~~~

Las tareas principales deben estar COMPLETED / 0:0. JobArrayTaskLimit es normal
para tareas pendientes cuando ya hay dos ejecutándose. Comprobar también el cierre:

~~~bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path("runs/alphas-small-001")
m = json.loads((base / "manifest.json").read_text())
for t in m["tasks"]:
    folder = base / f'task_{t["id"]:05d}'
    state = json.loads((folder / "finished.json").read_text())
    if state.get("success") is not True:
        raise SystemExit(f"Tarea incompleta o fallida: {folder}")
    if not state["root_files"]:
        raise SystemExit(f"Sin ROOT registrado: {folder}")
    print(folder.name, t["energy"], t["unit"], "OK")
print("Todas las tareas tienen cierre correcto.")
PY
~~~

No combinar archivos parciales de un TIMEOUT o de una tarea todavía activa.
Para inspeccionar una sola réplica completa se puede usar:

~~~bash
python3 scripts/plot_task.py runs/alphas-small-001 0
~~~

Eso analiza **dos eventos de 1 MeV**, no los veinte del grupo.

### E. Combinar por energía, nunca todas juntas

Estos comandos corresponden exactamente al mapa de 30 tareas anterior. Cada
patrón selecciona diez carpetas, una energía, y los archivos de workers de ese
grupo. Con un CPU por tarea se espera un archivo t0 por carpeta.

~~~bash
hadd -f runs/alphas-small-001/alpha_1MeV.root \
  runs/alphas-small-001/task_0000*/molecular-dna_t*.root

hadd -f runs/alphas-small-001/alpha_5MeV.root \
  runs/alphas-small-001/task_0001*/molecular-dna_t*.root

hadd -f runs/alphas-small-001/alpha_10MeV.root \
  runs/alphas-small-001/task_0002*/molecular-dna_t*.root
~~~

Cada archivo combinado debe contener **20 primarios**, no 60.
-f reemplaza un combinado previo con el mismo nombre sin modificar los originales.
Conservar las réplicas para analizar sus incertidumbres.

### F. Comprobar y graficar cada energía

**1 MeV:**

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_1MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_1MeV.root","runs/alphas-small-001/plots_1MeV")'
~~~

**5 MeV:**

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_5MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_5MeV.root","runs/alphas-small-001/plots_5MeV")'
~~~

**10 MeV:**

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_10MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_10MeV.root","runs/alphas-small-001/plots_10MeV")'
~~~

**Comprobación por grupo:** primary_source debe tener 20 filas, sin errores.
La macro debe informar partícula alpha, la energía correspondiente y 20 primarios.
Las filas de damage y classification pueden diferir de 20.

| Energía | Archivo combinado | Carpeta de figuras PNG/PDF |
| --- | --- | --- |
| 1 MeV | alpha_1MeV.root | plots_1MeV/ |
| 5 MeV | alpha_5MeV.root | plots_5MeV/ |
| 10 MeV | alpha_10MeV.root | plots_10MeV/ |

Todo queda dentro de runs/alphas-small-001/. Cada carpeta contiene
human_cell_alphas.png y human_cell_alphas.pdf.

**La macro es la misma para las tres energías; cambia el archivo de entrada.**
human_cell.mac configura la simulación; human_cell_alphas.C genera las gráficas.
No usar la macro de electrones para estas tareas ni fusionar las tres energías
en un único archivo para analizarlo como una sola condición.

Este procedimiento genera paneles separados por energía. Una curva conjunta
de rendimiento SSB/DSB frente a energía requiere un análisis comparativo adicional.
Las macros actuales muestran valores centrales sin barras de error: no sustituir
una incertidumbre no determinada por cero.

### G. Si las alfas vuelven a agotar el tiempo

Consultar simulation.log y sacct, además del máximo de la partición. No extrapolar
los tiempos de electrones a alfas. Si hay que cambiar el tiempo o los eventos,
editar el JSON y preparar otro directorio, por ejemplo runs/alphas-small-002.
No cambia la campaña ya enviada. La ejecución completa de esta configuración
de alfas debe verificarse con sus salidas reales; no se presenta como validada
solo porque haya funcionado la campaña de electrones.

config/scan.json mezcla partículas y energías: agrupar siempre por condición
física, usando el manifest, antes de combinar o graficar.

## 12. Lista final de comprobaciones

| Etapa | Condición para continuar |
| --- | --- |
| Setup | Versiones correctas, sin errores Spack/module |
| Copia | Fuentes y macro presentes |
| Geometría | Archivos verificados después de CMake |
| Build | `COMPLETED / 0:0` y ejecutable |
| Preparación | Manifest creado; eventos y semillas revisados |
| Envío | Cuenta p067, array y recursos correctos |
| Finalización | Tareas completas, `success: true` |
| ROOT | Primarios leídos iguales a los solicitados |
| Merge | Misma condición física y todos los workers pertinentes |
| Gráficas | PNG/PDF creados y normalización revisada |

[Prueba de 1,000 eventos](validation.md) · [Solución de problemas](troubleshooting.md) · [Fuentes y atribución](references.md) ·
[Publicación y mantenimiento](publishing.md)


<a id="alfas-vs-electrones"></a>
## Alfas frente a electrones: explicación opcional

En la campaña se generan primarios monoenergéticos: cada tarea tiene una sola
energía. El array distribuye las réplicas entre 1, 5 y 10 MeV. Tener tres energías
aumenta el número de tareas, no hace que una tarea transporte tres haces distintos.

Frente a los electrones de 0.662 MeV, las alfas de estas energías tienden a producir
trazas más cortas y rectas con ionizaciones más concentradas (mayor LET, energía
depositada por longitud). Se espera mayor tendencia al daño agrupado y complejo;
no es una garantía de que toda categoría de rendimiento por dosis aumente.

molecularDNA también simula la etapa química. Una traza densa puede elevar su costo
computacional y consumo de memoria. En la prueba se observó falta de memoria con
8 GB; todavía no se ha separado el costo de inicialización, transporte y química.
Atribuir el tiempo exclusivamente al LET sería una hipótesis, no una medición.

No hay una regla universal de tiempo o rendimiento creciente con energía:
cambian alcance, LET y energía depositada dentro de la región de interés.
Comparar por dosis, mantener la geometría y parámetros comunes y conservar réplicas.

Fuentes: [modelo químico de molecularDNA](https://geant4-dna.github.io/molecular-docs/docs/overview/chemistry-model.html)
y [estudio de LET y daño agrupado](https://pmc.ncbi.nlm.nih.gov/articles/PMC10810015/).

[Volver a la receta de alfas](alphas.md#7-qué-observar-frente-a-los-electrones)
