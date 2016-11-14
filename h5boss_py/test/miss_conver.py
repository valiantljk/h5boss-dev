from __future__ import division, print_function
import numpy as np
import os,sys
from h5boss import boss2hdf5
import pandas as pd
from mpi4py import MPI

df = pd.read_csv("h5boss_miss2",index_col=None,dtype=str,header=-1)
ldf=len(df)
def findseed(x):
     fitsfiles = [os.path.join(root, name)
       for root, dirs, files in os.walk(x)
       for name in files
        if name.startswith("spPlate") and name.endswith(".fits")]
     return fitsfiles

xian="/global/cscratch1/sd/jialin/bossfits/"
outputpath="/global/cscratch1/sd/jialin/h5boss/"
rank = MPI.COMM_WORLD.Get_rank()
nproc= MPI.COMM_WORLD.Get_size()

if rank<nproc:
  dir1=xian+df[0][rank]
  fitsf=findseed(dir1)
  try:
   hdf5file=fitsf[0].split('/')[-1].replace('spPlate-','',1).replace('fits','hdf5',1)
   boss2hdf5.serial_convert(fitsf,outputpath+hdf5file)
  except Exception as e:
   print ("no spPlate in dir1")
   pass
