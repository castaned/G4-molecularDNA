---
layout: default
title: Receta para alfas
---

# Alfas: resultados separados para tres energías

[Volver al inicio](index.md)

**Objetivo:** simular alfas de 1, 5 y 10 MeV y obtener una gráfica para cada energía.
Usaremos dos eventos por trabajo porque estas simulaciones pueden tardar más.

El ejemplo debe estar compilado. Abre una terminal de YUCA:

~~~bash
cd ~/G4-molecularDNA
source env/setup.sh
~~~

## 1. Crear la configuración

Copia el bloque completo, desde python3 hasta la última línea PY:

~~~bash
python3 - <<'PY'
import json
from pathlib import Path
cfg = json.loads(Path("config/alphas.json").read_text())
cfg.update(name="alphas-small", particles=["alpha"], energies=[1, 5, 10],
           unit="MeV", events_per_job=2, replicas=10, seed_base=80001)
cfg["resources"].update(cpus=1, memory="32G", time="12:00:00",
                        max_concurrent=1, account="p002")
Path("config/alphas-small.local.json").write_text(json.dumps(cfg, indent=2) + "\n")
PY
~~~

**Debe ocurrir:** vuelve a aparecer el cursor sin errores.
Esto prepara 30 trabajos: diez por energía, con dos eventos cada uno.
Cada energía tendrá veinte eventos. Se ejecuta **un trabajo a la vez**, con
**32 GB y hasta doce horas por trabajo**. Se usan 32 GB como prueba porque una
alfa agotó los 8 GB; todavía hay que comprobar si ese límite es suficiente.

## 2. Preparar y enviar

~~~bash
python3 scripts/campaign.py prepare config/alphas-small.local.json runs/alphas-small-001 &&
python3 scripts/campaign.py submit runs/alphas-small-001 --dry-run
~~~

**Comprueba:** aparecen --array=0-29%1, --mem=32G y --account=p002.

~~~bash
python3 scripts/campaign.py submit runs/alphas-small-001
~~~

Anota el número recibido. Si ya usaste esta carpeta en otro intento, cambia
alphas-small-001 por alphas-small-002 en todos los comandos.
No se necesita recompilar.

## 3. Esperar a que terminen

Sustituye NUMERO por el número recibido:

~~~bash
squeue -r -j NUMERO
sacct -j NUMERO --format=JobID%25,State%18,ExitCode,Elapsed,MaxRSS
~~~

| Qué ves | Qué hacer |
| --- | --- |
| Un trabajo RUNNING y los demás PENDING | Es lo esperado: se permite uno a la vez |
| JobArrayTaskLimit | Esperar; no es un error |
| COMPLETED y 0:0 | Esa tarea terminó correctamente |
| OUT_OF_MEMORY | Le faltó memoria; no combinar su ROOT |
| TIMEOUT | Agotó el tiempo; no combinar su ROOT |

Para ver el avance de la primera tarea:

~~~bash
tail -f runs/alphas-small-001/task_00000/simulation.log
~~~

**Qué esperar:** puede quedarse en Event 0 o en el inicio del modelo químico
durante bastante tiempo. Eso solo no demuestra que esté detenido. Sal de esta
vista con **Ctrl+C**; la simulación seguirá corriendo.

Para consultar memoria y tiempo de CPU de esa tarea:

~~~bash
sstat -j NUMERO_0.0 --format=JobID,AveCPU,AveRSS,MaxRSS
~~~

Si aún no muestra datos, consulta de nuevo más tarde. MaxRSS es el máximo
observado por el sistema de contabilidad; no garantiza que haya capturado
todos los picos de memoria.

**Cada job usa una sola energía**, no recorre las tres: tareas 0–9 a 1 MeV,
10–19 a 5 MeV y 20–29 a 10 MeV. Son las tareas del array las que se reparten
entre esas energías.

**Espera a que los treinta trabajos estén COMPLETED y 0:0** antes del paso 4.
Si hay un fallo, abre [solución de problemas](troubleshooting.md).
Cambiar la configuración no modifica los trabajos que ya están enviados.

## 4. Combinar cada energía por separado

**No combines las tres energías en un solo archivo.** Para la configuración
que acabas de crear, los grupos son:

| Energía | Carpetas | Eventos combinados |
| --- | --- | --- |
| 1 MeV | task_00000 a task_00009 | 20 |
| 5 MeV | task_00010 a task_00019 | 20 |
| 10 MeV | task_00020 a task_00029 | 20 |

Copia estos comandos después de que terminen todos:

~~~bash
hadd -f runs/alphas-small-001/alpha_1MeV.root \
  runs/alphas-small-001/task_0000*/molecular-dna_t*.root

hadd -f runs/alphas-small-001/alpha_5MeV.root \
  runs/alphas-small-001/task_0001*/molecular-dna_t*.root

hadd -f runs/alphas-small-001/alpha_10MeV.root \
  runs/alphas-small-001/task_0002*/molecular-dna_t*.root
~~~

**Debe ocurrir:** aparecen tres archivos: alpha_1MeV.root, alpha_5MeV.root
y alpha_10MeV.root. No borres las carpetas individuales.
-f reemplaza los combinados si ya existían.

## 5. Comprobar y graficar

### Alfas de 1 MeV

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_1MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_1MeV.root","runs/alphas-small-001/plots_1MeV")'
~~~

### Alfas de 5 MeV

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_5MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_5MeV.root","runs/alphas-small-001/plots_5MeV")'
~~~

### Alfas de 10 MeV

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/alphas-small-001/alpha_10MeV.root",20)' &&
root -l -b -q 'analysis/human_cell_alphas.C("runs/alphas-small-001/alpha_10MeV.root","runs/alphas-small-001/plots_10MeV")'
~~~

**Debe ocurrir en cada grupo:** primary_source: 20 filas, y se crean un PNG y un PDF.

## 6. Abrir las figuras

En el explorador del escritorio YUCA, entra en G4-molecularDNA/runs/alphas-small-001/.

| Energía | Carpeta |
| --- | --- |
| 1 MeV | plots_1MeV/ |
| 5 MeV | plots_5MeV/ |
| 10 MeV | plots_10MeV/ |

En cada una encontrarás human_cell_alphas.png y human_cell_alphas.pdf.

**Ya completaste la receta cuando las tres comprobaciones y gráficas terminan
sin error.** La macro es la misma; cambia el archivo de entrada.

## 7. Qué observar frente a los electrones

Abre los tres PNG de alfas y el PNG de electrones. Usa esta lista:

| Mira | Qué comparar |
| --- | --- |
| Number of Primaries | Veinte por energía alfa; no confundir con el total de registros de daño |
| Dose Absorbed | La misma cantidad de partículas no produce necesariamente la misma dosis |
| Damage yield | Comparar SSB, DSB y categorías complejas usando las mismas unidades del eje |
| Las tres energías | Anotar los valores por separado; no esperar que aumenten siempre de 1 a 10 MeV |

**Las alfas tienden a concentrar más el daño cerca de su trayectoria.** Por eso
pueden exigir más memoria y tiempo que los electrones. No significa que el
job esté calculando las tres energías a la vez, ni que la energía mayor tarde
siempre más.

Con solo veinte alfas por energía pueden quedar categorías en cero y verse
fluctuaciones grandes. No concluir que una categoría no existe por obtener
cero en esta muestra.

**Comparar valores por dosis, no solo el número bruto de daños.** Las figuras
muestran valores centrales; las incertidumbres requieren un análisis adicional.
La distribución espacial de los daños no se ve directamente en estos cuatro
paneles: para estudiarla se necesita otro análisis.

La explicación física es opcional: [ver referencia técnica](advanced.md#alfas-vs-electrones).

<details>
<summary>Si quiero cambiar energías o número de trabajos</summary>

Esta receta y sus grupos de carpetas corresponden exactamente a 1, 5 y 10 MeV,
en ese orden, con diez réplicas por energía. Si cambias esos valores, consulta
el manifest y adapta el agrupamiento antes de combinar. La
[explicación técnica](advanced.md#alfas) contiene el procedimiento detallado.

Doce horas son un límite inicial, no una predicción. Dos eventos por trabajo
no garantizan que una configuración cualquiera termine en ese tiempo.
Se conservan las réplicas para poder evaluar incertidumbres.

</details>
