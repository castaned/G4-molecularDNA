#!/usr/bin/env bash
#SBATCH --job-name=g4dna-build
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
set -euo pipefail
# Enviar desde la raíz: sbatch [--partition=...] slurm/build.slurm
bash scripts/build.sh
