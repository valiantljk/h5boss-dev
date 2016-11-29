#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 1 
#SBATCH -t 00:10:00
#SBATCH -J subset-mpi
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -L SCRATCH
#SBATCH -C haswell
#SBATCH --ntasks-per-node=32
cd $SLURM_SUBMIT_DIR
# below is the added line. Must be after the module command!
# source /project/projectdirs/m779/python-mpi/nersc/activate.sh

# Control Arguments:
version="_v1" # or "_v2"
cmdscript="../scripts/subset_mpi"$version".py "
nproc="32"
#cmd="srun -n "$nproc" python-mpi -m memory_profiler "$cmdscript
cmd="srun -n "$nproc" python-mpi "$cmdscript

# Positional Arguments:
srcfile=" input_csv/input-full-cori"$version" "
template=$CSCRATCH/bosslover/scaling-test/ost1/$SLURM_JOB_ID.h5
randpmf=$SLURM_JOB_ID.txt
npmf=1000
#shuf -n $npmf pmf-list/large-scale/pmf500k -o pmf-list/large-scale/$randpmf
#sed -i '1i\'"plates mjds fibers" pmf-list/large-scale/$randpmf
#pmfquery=" pmf-list/large-scale/"$randpmf" "
pmfquery=" pmflist/1k_nov2 "
# Optional Arguments:
k_opt1=" --mpi="         # 'yes' for parallel read/wirte 
                         # 'no'  for serial read/write

k_opt2=" --template="    # 'yes' for creating a template only 
 		         # 'no'  for using previous template and writing the actual data into it
		         # 'all' for creating a template and writing the actual data into it

k_opt3=" --fiber="       # specify a file that could store the accessed fiber information
k_opt4=" --catalog="     # specify a file that could store the accssed catalog information
k_opt5=" --datamap="     # specify a file that stored all fiber information of source files
                         # if not specified, will scan all source files to create a new datamap

v_opt1="yes "
v_opt2="all "
v_opt3=$SLURM_JOB_ID"_fiber.txt "
v_opt4=$SLURM_JOB_ID"_catalog.txt "
v_opt5="all.pk"



#run=$cmd$srcfile$template$pmfquery$k_opt1$v_opt1$k_opt2$v_opt2$k_opt3$v_opt3$k_opt4$v_opt4$k_opt5$v_opt5
run=$cmd$srcfile$template$pmfquery$k_opt1$v_opt1$k_opt2$v_opt2$k_opt3$v_opt3$k_opt4$v_opt4
echo $run >>${SLURM_JOB_ID}.err
echo $run
$run
