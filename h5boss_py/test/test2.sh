#!/bin/bash
#SBATCH -p regular 
#SBATCH -N 1 
#SBATCH -t 12:30:00
#SBATCH -J subset-mpi
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -L SCRATCH
#SBATCH -C haswell
#SBATCH --ntasks-per-node=32
##SBATCH --qos=premium
##SBATCH -A mpccc

cd $SLURM_SUBMIT_DIR
version="_v1" # or "_v2"
cmdscript="../scripts/subset_mpi"$version".py "
nproc="2"
cmd="srun -n "$nproc" python-mpi "$cmdscript
srcfile=" inputv1 "
pmf=100k_nov2
template=$CSCRATCH/h5boss_pre/$pmf_1node_p2.h5
pmfquery=" pmflist/"$pmf" "
# Optional Arguments:
k_opt1=" --mpi="         # 'yes' for parallel read/wirte 
                         # 'no'  for serial read/write

k_opt2=" --template="    # 'yes' for creating a template only 
 		         # 'no'  for using previous template and writing the actual data into it
		         # 'all' for creating a template and writing the actual data into it
v_opt1="yes "
v_opt2="all "

run=$cmd$srcfile$template$pmfquery$k_opt1$v_opt1$k_opt2$v_opt2
echo $run
$run
