#!/usr/bin/env bash
#SBATCH --account=p002
# Los recursos y el array se definen en scripts/campaign.py submit.
set -euo pipefail
repo="$1"
campaign="$2"
source "$repo/env/setup.sh"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
# sbatch de esta campaña usa --mem (memoria por nodo). Open OnDemand puede
# exportar memoria por CPU/GPU de su propia asignación; no pasarla al step.
: "${SLURM_MEM_PER_NODE:?La campaña debe solicitar memoria mediante --mem}"
env -u SLURM_MEM_PER_CPU -u SLURM_MEM_PER_GPU \
  srun --mem="$SLURM_MEM_PER_NODE" --ntasks=1 --cpus-per-task="$SLURM_CPUS_PER_TASK" \
  python3 "$repo/scripts/campaign.py" run-task "$campaign" "$SLURM_ARRAY_TASK_ID"
