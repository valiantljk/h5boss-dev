#!/usr/bin/env python
"""
MPI version of get_fiber map, return all dataset as k,v(plate/mjd/fiber/../dataset, (type,shape,filename_path))
"""
from __future__ import division, print_function
import cPickle as pickle
import hickle as hkl
from collections import defaultdict
import h5py
import time
import os,sys
from h5boss.h5map import map_fiber_simple
from h5boss.selectmpi_v1 import add_dic
from mpi4py import MPI 

pkfile="allfiber.pk"
hkfile="allfiber.hk"
pkfilesimple="allfiber.pksim"
hkfilesimple="allfiber.hksim"
dirpath="/global/cscratch1/sd/jialin/h5boss"
mapdir="/global/cscratch1/sd/jialin/h5boss/map/"
comm=MPI.COMM_WORLD
nproc= comm.Get_size()
rank= comm.Get_rank()
allfiles_paths = [os.path.join(dirpath,fn) for fn in next(os.walk(dirpath))[2]][0:nproc]
total_files=len(allfiles_paths)
if rank==0:
 print ("number of hdf5 files: %d\n"%total_files)
 print ("number of processes: %d\n"%nproc)
 assert(nproc==total_files)
fiber_item={}
global_time=0
ifile=allfiles_paths[rank]

tstart=MPI.Wtime()
try:
  fiber_item = map_fiber_simple(ifile)
except Exception as e:
  print ("error in file %s"%(ifile)) 
  pass 
tend=MPI.Wtime()
    
print ("Rank: %d, File:%s, Scanning: %d, Dataset_objects_cost: %f\n"%(rank,ifile,len(fiber_item),tend-tstart))
comm.Barrier()
tpkstart=time.time()
try:
 pickle.dump(fiber_item,open(mapdir+pkfilesimple+"_"+str(rank),"wb"))
 #hkl.dump(fiber_item,mapdir+hkfile+"_"+str(rank),mode="w")
except Exception as e:
 print ("pickle error")
 pass
tpkend=time.time()
#print ("Rank: %d, Pickling_cost: %f\n"%(rank,tpkend-tpkstart))

comm.Barrier()
counterop = MPI.Op.Create(add_dic, commute=True)
treduce=MPI.Wtime()
#global_fiber_dms= comm.allreduce(global_fiber_dm, op=counterop)
treduceend=MPI.Wtime()-treduce
if rank==0:
 print("Total cost:%f"%(treduceend))
#tpkstart=time.time()
#try:
# hkl.dump(fiber_item,mapdir+hkfilesimple+"_"+str(rank),mode="w")
#except Exception as e:
# print ("pickle error")
# pass
#tpkend=time.time()
#print ("Rank: %d, Hickling_cost: %f\n"%(rank,tpkend-tpkstart))


