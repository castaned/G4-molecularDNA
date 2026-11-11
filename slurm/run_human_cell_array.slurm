#!/usr/bin/env bash
#SBATCH --account=p002
# Los recursos y el array se definen en scripts/campaign.py submit.
set -euo pipefail
repo="$1"
campaign="$2"
source "$repo/env/setup.sh"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
srun --ntasks=1 --cpus-per-task="$SLURM_CPUS_PER_TASK" \
  python3 "$repo/scripts/campaign.py" run-task "$campaign" "$SLURM_ARRAY_TASK_ID"
