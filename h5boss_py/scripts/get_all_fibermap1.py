#!/usr/bin/env python
"""
MPI version of get_fiber map, return all dataset as k,v(plate/mjd/fiber/../dataset, (type,shape,filename_path))
"""
from __future__ import division, print_function
import cPickle as pickle
from collections import defaultdict
import h5py
import time
import os,sys
from h5boss.h5map import map_fiber
from h5boss.selectmpi_v1 import add_dic
from mpi4py import MPI 

pkfile="allfiber.pk"
dirpath="/global/cscratch1/sd/jialin/h5boss"
mapdir="/global/cscratch1/sd/jialin/h5boss/map/"
comm=MPI.COMM_WORLD
nproc= comm.Get_size()
rank= comm.Get_rank()
allfiles_paths = [os.path.join(dirpath,fn) for fn in next(os.walk(dirpath))[2]]
total_files=len(allfiles_paths)
if rank==0:
 print ("number of hdf5 files: %d\n"%total_files)
 print ("number of processes: %d\n"%nproc)
fiber_item={}
global_time=0
ifile=allfiles_paths[rank]

tstart=MPI.Wtime()
try:
  fiber_item = map_fiber(ifile)
except Exception as e:
  print ("error in file %s"%(ifile)) 
  pass 
tend=MPI.Wtime()
    
print ("Rank: %d, File:%s, Scanning: %d, Dataset_objects_cost: %f\n"%(rank,ifile,len(fiber_item),tend-tstart))
comm.Barrier()
tpkstart=time.time()
try:
 pickle.dump(fiber_item,open(mapdir+pkfile+"_"+str(rank),"wb"))
except Exception as e:
 print ("pickle error")
 pass
tpkend=time.time()
print ("Rank: %d, Pickling_cost: %f\n"%(rank,tpkend-tpkstart))
