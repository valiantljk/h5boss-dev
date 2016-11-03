#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 1 
#SBATCH -t 00:10:00
#SBATCH -J subset-fits-h5
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -L SCRATCH
#SBATCH -C haswell
#SBATCH --ntasks-per-node=32
cd $SLURM_SUBMIT_DIR

pmf=pmflist/1k-nov2 #pmflist/pmf10 100-nov2 1k-nov2 10k-nov2 100k-nov2 500k-nov2
#TODO: query 1k from 10k.h5, so needs sub-select pmf from 10k-nov2
pre=/global/cscratch1/sd/jialin/h5boss_pre/1k.h5 #TODO: 10.h5 100.h5 10k.h5 100k.h5 1m.h5(1TB)
var=FLUX # WAVE 
#case 1: WAVE and FLUX only
#TODO: rewrite the code to support case 2 and 3
	#case 2: WAVE, FLUX, IVAR, and MASK
	#case 3: all columns
#TODO: generate pre-selected files, can be pipelined with the subsetting scaling test

#h5b test with pre-selected file
cmd1="python test_h5bossread_pmf.py "$pmf" "$var" "$pre

#h5b test with source files only 
cmd2="python test_h5bossread_pmf.py "$pmf" "$var" none"

#fits test
cmd3="python test_fitsread_pmf.py "$pmf" flux"

echo $cmd1
$cmd1
echo $cmd2
$cmd2
echo $cmd3
$cmd3

