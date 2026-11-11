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
cfg["resources"].update(cpus=1, memory="8G", time="12:00:00",
                        max_concurrent=2, account="p002")
Path("config/alphas-small.local.json").write_text(json.dumps(cfg, indent=2) + "\n")
PY
~~~

**Debe ocurrir:** vuelve a aparecer el cursor sin errores.
Esto prepara 30 trabajos: diez por energía, con dos eventos cada uno.
Cada energía tendrá veinte eventos. Se permiten dos trabajos simultáneos y
hasta doce horas por trabajo.

## 2. Preparar y enviar

~~~bash
python3 scripts/campaign.py prepare config/alphas-small.local.json runs/alphas-small-001 &&
python3 scripts/campaign.py submit runs/alphas-small-001 --dry-run
~~~

**Comprueba:** aparecen --array=0-29%2 y --account=p002.

~~~bash
python3 scripts/campaign.py submit runs/alphas-small-001
~~~

Anota el número recibido. Si ya usaste esta carpeta en otro intento, cambia
alphas-small-001 por alphas-small-002 en todos los comandos.
No se necesita recompilar.

## 3. Esperar a que terminen

Sustituye NUMERO por el número recibido:

~~~bash
sacct -j NUMERO --format=JobID,State,ExitCode
~~~

**Espera a que los treinta trabajos estén COMPLETED y 0:0.**
PENDING y JobArrayTaskLimit no son fallos: los trabajos esperan su turno.
Si aparece FAILED o TIMEOUT, abre [solución de problemas](troubleshooting.md).

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
