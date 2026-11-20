---
layout: default
title: Daño de protones frente al LET
---

# Daño en ADN de protones en función del LET

[Volver a la receta de protones](protons.md)

Referencia: Shin et al., Cancers 2021, 13, 4940, figuras 3 y 4 y tabla 3
(https://doi.org/10.3390/cancers13194940).

## 1. Preparar un barrido piloto en YUCA

Usa una campaña independiente por energía. La receta sirve para comprobar el
análisis con 100 primarios por punto; amplía la estadística según la precisión de DSB.
**Actualiza el repositorio antes de copiar el bloque del barrido.** En YUCA, ejecuta:

```bash
cd ~/G4-molecularDNA && git pull --ff-only
```

Continúa cuando el comando termine correctamente. Si ves
`ERROR: 'max_concurrent'`, tu copia de `scripts/campaign.py` es anterior al cambio
que hizo opcional ese campo. Actualiza el repositorio y vuelve a ejecutar el bloque
completo desde `BASE=...` para preparar el barrido en una carpeta nueva.

Ahora prepara el barrido:

```bash
source env/setup.sh
BASE="runs/proton-let-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BASE"
for E in 1 2 5 10 20; do
  python3 - "$E" "$BASE" <<'PY'
import json
from pathlib import Path
import sys

energy, base = int(sys.argv[1]), Path(sys.argv[2])
cfg = json.loads(Path("config/protons.json").read_text())
cfg.update(name=f"proton-let-{energy}mev", energies=[energy],
           events_per_job=10, replicas=10, seed_base=200000 + 1000 * energy)
cfg["resources"].update(account="p067", memory="10G", cpus=1)
cfg["resources"].pop("max_concurrent", None)
(base / f"proton-{energy}mev.json").write_text(json.dumps(cfg, indent=2))
PY
  [[ $? -eq 0 ]] || break
  RUN="$BASE/proton-${E}mev"
  python3 scripts/campaign.py prepare "$BASE/proton-${E}mev.json" "$RUN" &&
  python3 scripts/campaign.py submit "$RUN" --dry-run || break
done
```

Comprueba que aparezcan `--account=p067`, `--mem=10G` y `--array=0-9`.
Tras revisar el tiempo y los recursos, envía cada campaña con
`python3 scripts/campaign.py submit "$BASE/proton-10mev"`, cambiando la
energía en el nombre. Guarda los identificadores que devuelve Slurm.

## 2. Validar y analizar cada energía

Confirma con `sacct` que cada una de las diez tareas del punto terminó en
`COMPLETED` con código `0:0`. Analiza una energía cada vez:

```bash
RUN="$BASE/proton-10mev"
MERGED="$RUN/combined.root"
INPUTS=("$RUN"/task_0000{0..9}/molecular-dna_t0.root)
hadd "$MERGED" "${INPUTS[@]}" &&
root -l -b -q "analysis/inspect_output.C(\"$MERGED\",100)" &&
root -l -b -q "analysis/human_cell_proton.C(\"$MERGED\",\"$RUN/plots_combined\")"
```

Repite por energía. Conserva también los ROOT individuales y el manifiesto.

## 3. Construir los puntos de la curva

Usa el LET en agua de ICRP 90 del artículo para las energías que figuren en
su tabla 3. Para energías adicionales, documenta la fuente de LET, el método
de interpolación cuando corresponda y si se usa la energía incidente. Registra
el LET en keV/µm. La dosis se calcula a partir de la energía depositada en el
volumen de análisis y su masa.

Para cada condición, divide la suma de los conteos por la dosis acumulada y
por el contenido de ADN en Gbp. La razón SSB/DSB usa los conteos de la misma
condición. Si DSB es cero, deja la razón sin valor. Para estimar intervalos,
remuestrea réplicas completas y recalcula el cociente con sus dosis y conteos.
Amplía el número de réplicas si los DSB son demasiado escasos para estimar
una incertidumbre útil.

| Gráfica | Datos por punto |
| --- | --- |
| Tipo figura 3 | Roturas de hebra **elementales** totales, directas e indirectas, en Gy⁻¹ Gbp⁻¹ |
| Tipo figura 4 | Rendimientos de SSB y DSB clasificados, en Gy⁻¹ Gbp⁻¹, y razón SSB/DSB |

Para la figura 3, valida en el árbol de daño cómo identificar roturas de
hebra elementales, incluidas las que forman parte de un DSB. Documenta cómo
tratas una rotura con contribución de ambos mecanismos. Los totales de SSB
que imprime la macro corresponden a categorías de daño.

## 4. Exportar a CSV y graficar con PyROOT

Crea `proton_let_inputs.csv` con estas columnas:

```csv
energy_mev,let_kev_um,let_source,root_file
```

Añade una fila por energía con el LET numérico en agua, su fuente y la ruta
del ROOT combinado. Las rutas relativas se resuelven desde el directorio del
CSV. Usa al menos dos energías y un archivo distinto por fila. La energía y
el LET se toman de este índice, así que verifica que correspondan al ROOT.

```bash
source env/setup.sh
python3 -c 'import ROOT; print(ROOT.gROOT.GetVersion())'
python3 scripts/plot_proton_let.py proton_let_inputs.csv results/proton-let
```

La macro existente extrae de cada ROOT el número de primarios, la dosis y
los conteos clasificados. El script consolida los puntos en `proton_let.csv`
y genera `proton_damage_vs_let.png` y `.pdf` con PyROOT. Esta versión
produce los tres paneles de la figura 4 con valores centrales: SSB, DSB y
SSB/DSB. Cuando DSB es cero, la razón queda vacía en el CSV y se omite del panel.
La figura 3 requiere validar por separado el conteo elemental descrito arriba.
