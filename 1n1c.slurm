#!/bin/bash
#SBATCH --partition=physical
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time 24:00:00
module load foss/2019b
module load python/3.7.4
module load mpi4py/3.0.2-timed-pingpong
srun -n 1 python3 TheHappiestCity5.py