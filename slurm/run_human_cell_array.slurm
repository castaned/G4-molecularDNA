#!/usr/bin/env bash
# La cuenta se toma de resources.account en la configuración de la campaña.
# Los recursos y el array se definen en scripts/campaign.py submit.
set -euo pipefail
repo="$1"
campaign="$2"
python_bin="${3:?Falta la ruta absoluta de Python; enviar mediante campaign.py submit}"
source "$repo/env/setup.sh"
[[ "$python_bin" == /* && -x "$python_bin" ]] || { echo "Python no está disponible en el nodo $(hostname): $python_bin. Usar un intérprete instalado en una ruta compartida de YUCA." >&2; exit 1; }
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
# sbatch de esta campaña usa --mem (memoria por nodo). Open OnDemand puede
# exportar memoria por CPU/GPU de su propia asignación; no pasarla al step.
: "${SLURM_MEM_PER_NODE:?La campaña debe solicitar memoria mediante --mem}"
env -u SLURM_MEM_PER_CPU -u SLURM_MEM_PER_GPU \
  srun --export=ALL --mem="$SLURM_MEM_PER_NODE" --ntasks=1 --cpus-per-task="$SLURM_CPUS_PER_TASK" \
  "$python_bin" "$repo/scripts/campaign.py" run-task "$campaign" "$SLURM_ARRAY_TASK_ID"
