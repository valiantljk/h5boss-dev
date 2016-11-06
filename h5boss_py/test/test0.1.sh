#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 1 
#SBATCH -t 00:10:00
#SBATCH -J bossmiss 
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -L SCRATCH

srun -n 24 python-mpi  miss_conver.py

