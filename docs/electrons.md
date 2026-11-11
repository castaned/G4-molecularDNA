---
layout: default
title: Receta para electrones
---

# Electrones: de la simulación a las gráficas

[Volver al inicio](index.md)

Abre una terminal de YUCA y entra al repositorio. El ejemplo debe estar compilado:

~~~bash
cd ~/G4-molecularDNA
source env/setup.sh
~~~

**Usa una carpeta nueva para cada intento.** Si ya existe el nombre indicado,
cámbialo en todos los comandos de ese recorrido; por ejemplo, usa electrons-002.

<a id="prueba"></a>
## Primero: una prueba de dos eventos

Si ya comprobaste que la simulación funciona, salta al apartado
[Generar 1,000 eventos](#campana).

~~~bash
python3 scripts/campaign.py prepare config/smoke.json runs/smoke-001 &&
python3 scripts/campaign.py submit runs/smoke-001
~~~

Anota el número que aparece después de Enviada campaña.
Para revisar, sustituye NUMERO por ese número:

~~~bash
sacct -j NUMERO --format=JobID,State,ExitCode
~~~

**Espera a ver COMPLETED y 0:0.** Después:

~~~bash
python3 scripts/plot_task.py runs/smoke-001 0
~~~

**Debe ocurrir:** se comprueban dos primarios y se crean archivos PNG y PDF en
runs/smoke-001/task_00000/plots/.

<a id="campana"></a>
## 1. Generar 1,000 eventos

La configuración incluida ya está preparada: diez trabajos de cien electrones,
todos a 0.662 MeV. Solo se ejecutan dos trabajos simultáneamente.

~~~bash
python3 scripts/campaign.py prepare config/electrons.json runs/electrons-001 &&
python3 scripts/campaign.py submit runs/electrons-001 --dry-run
~~~

**Comprueba:** aparecen --array=0-9%2 y --account=p002.

Ahora envía:

~~~bash
python3 scripts/campaign.py submit runs/electrons-001
~~~

Anota el número recibido.

## 2. Esperar a que terminen los diez trabajos

Sustituye NUMERO por el número recibido:

~~~bash
sacct -j NUMERO --format=JobID,State,ExitCode
~~~

**Continúa solo cuando los diez trabajos estén COMPLETED y 0:0.**
Si algunos están pendientes, espera: no tienes que enviarlos de nuevo.

<details>
<summary>¿Qué significan los estados?</summary>

| Estado | Significado |
| --- | --- |
| RUNNING | Está trabajando |
| PENDING | Espera su turno |
| JobArrayTaskLimit | Ya están trabajando los dos permitidos |
| COMPLETED y 0:0 | Terminó sin error de Slurm |
| FAILED o TIMEOUT | Revisar el error antes de continuar |

Las filas .batch y .0 son partes internas del mismo trabajo, no trabajos adicionales.

</details>

## 3. Combinar los resultados

~~~bash
hadd -f runs/electrons-001/electrons_1000.root \
  runs/electrons-001/task_*/molecular-dna_t0.root
~~~

**Debe ocurrir:** se crea electrons_1000.root. No borres los archivos individuales.
Si ya existía ese combinado, -f lo reemplaza.

## 4. Comprobar y graficar

~~~bash
root -l -b -q 'analysis/inspect_output.C("runs/electrons-001/electrons_1000.root",1000)' &&
root -l -b -q 'analysis/human_cell_electron.C("runs/electrons-001/electrons_1000.root","runs/electrons-001/plots_combined")'
~~~

**Debe ocurrir:** aparece primary_source: 1000 filas y ROOT confirma la creación
de un PNG y un PDF.

## 5. Abrir las figuras

En el explorador de archivos del escritorio YUCA, abre:

~~~text
G4-molecularDNA/runs/electrons-001/plots_combined/
~~~

Las figuras se llaman human_cell_electron.png y human_cell_electron.pdf.

**Ya completaste la receta.** Este recorrido funcionó en YUCA:
[ver el registro de la prueba](validation.md).

<details>
<summary>Quiero cambiar eventos o semillas</summary>

Edita config/electrons.json antes de preparar otra campaña.

| Cambiar | Campo |
| --- | --- |
| Eventos por trabajo | events_per_job |
| Número de trabajos por energía | replicas |
| Semillas | seed_base |
| Tiempo máximo por trabajo | resources.time |

Cada trabajo recibe semillas distintas. Para otra campaña independiente, elige
otro intervalo de semillas. Los cambios no afectan a una campaña ya preparada.

</details>

Si algo falla: [solución de problemas](troubleshooting.md).
