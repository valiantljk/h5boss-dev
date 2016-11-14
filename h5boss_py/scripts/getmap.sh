#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH -J h5map
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -V
#SBATCH -A mpccc
#SBATCH -C haswell
cd $SLURM_SUBMIT_DIR
srun -n 32 python-mpi get_all_fibermap1.py
