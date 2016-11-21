#!/bin/bash
#SBATCH -p regular 
#SBATCH -N 7
#SBATCH -t 00:30:00
#SBATCH -J h5map
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -A mpccc
#SBATCH -C haswell
cd $SLURM_SUBMIT_DIR
#2442
#320
#srun -n 640 python-mpi get_all_fibermap1.py 321 allfiber_961   # 321+640=961

#srun -n 640 python-mpi get_all_fibermap1.py 962 allfiber_1602  # 962+640=1602

#srun -n 640 python-mpi get_all_fibermap1.py 1603 allfiber_2243 # 1603+640=2243

srun -n 198 python-mpi get_all_fibermap1.py 2244 allfiber_2442  # 2244+199=2244
