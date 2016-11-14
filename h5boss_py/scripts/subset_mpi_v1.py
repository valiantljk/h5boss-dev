#!/usr/bin/env python
"""
Create an HDF5 file from BOSS data

TODO:
  - include comments in meta/attrs
  - platelist quantities
"""
from __future__ import division, print_function
#from __future__ import absolute_import
from mpi4py import MPI
import h5py
from h5boss.pmf import parse_csv
from h5boss.pmf import get_fiberlink_v1
from h5boss.pmf import get_catalogtypes
from h5boss.pmf import count_unique
from h5boss.pmf import locate_fiber_in_catalog
from h5boss.selectmpi_v1 import add_dic
from h5boss.selectmpi_v1 import add_numpy
from h5boss.selectmpi_v1 import create_template
from h5boss.selectmpi_v1 import overwrite_template
from time import gmtime, strftime
import datetime
import sys,os
import time
import optparse
import csv
import traceback
#import pandas as pd
import numpy as np
import optparse
import argparse
import datetime
from collections import defaultdict
import cPickle as pickle
from copy import deepcopy
#@profile
#def parallel_search():

def parallel_select():
    '''
    Select a set of (plates,mjds,fibers) from the realesed BOSS data in HDF5 formats.
    
    Args:
        input:   HDF5 files list, i.e., source data, [csv file]
        output:  HDF5 file, to be created or updated
        pmf: Plates/mjds/fibers numbers to be quried, [csv file]
       
    '''
    parser = argparse.ArgumentParser(prog='subset_mpi')
    parser.add_argument("input",  help="HDF5 input list")
    parser.add_argument("output", help="HDF5 output")
    parser.add_argument("pmf",    help="Plate/mjd/fiber list")
    parser.add_argument("--template", help="Create template only,yes/no/all")
    parser.add_argument("--mpi", help="using mpi yes/no")
    parser.add_argument("--fiber", help="specify fiber csv output")
    parser.add_argument("--catalog", help="specify catalog csv output")
    parser.add_argument("--datamap", help="specify datamap hickle file")
    opts=parser.parse_args()

    infiles = opts.input
    outfile = opts.output
    pmflist = opts.pmf
    fiberout = "fibercsv"
    catalogout = "catalogcsv"
    datamap=""
    if opts.datamap:
     datamap=opts.datamap
    if opts.fiber:
     fiberout = opts.fiber
    if opts.catalog:
     catalogout = opts.catalog
    catalog_meta=['plugmap', 'zbest', 'zline',
                        'match', 'matchflux', 'matchpos']
    meta=['plugmap', 'zbest', 'zline',
                        'photo/match', 'photo/matchflux', 'photo/matchpos']
    if opts.template is None or opts.template=="no":
       template=0
    elif opts.template and opts.template=="yes":
       template=1
    elif opts.template and opts.template=="all":
       template=2
    if opts.mpi is None or opts.mpi=="no": 
        print ("Try the subset.py or subset command")
        sys.exit()
    elif opts.mpi and opts.mpi=="yes":
        comm =MPI.COMM_WORLD
        nproc = comm.Get_size()
        rank = comm.Get_rank()
##_________________ Query _________________ ##
        tstartcsv=MPI.Wtime()
        (plates,mjds,fibers,hdfsource) = parse_csv(infiles, outfile, pmflist,rank)
        tstart=MPI.Wtime()
        total_files=len(hdfsource)
        global_fiber={}
        ok_global=0
        if (opts.datamap):
            #check if hickle file exists:
            if (os.path.exists(datamap)):
               global_fiber=query_datamap(datamap,plates,mjds,fibers,infiles) #abort if datamap is not complete, e.g., file not matching with infiles
               ok_global=1
        if(ok_global==0):               
         #distribute the workload evenly
         step=int(total_files / nproc)
         rank_start =int( rank * step)
         rank_end = int(rank_start + step)
         if(rank==nproc-1):
             #adjust the last rank's range
             rank_end=total_files
             if rank_start>total_files:
              rank_start=total_files
         range_files=hdfsource[rank_start:rank_end]
         if rank==0:
           sample_file=range_files[0]
         fiber_dict={}
         for i in range(0,len(range_files)):
             fiber_item = get_fiberlink_v1(range_files[i],plates,mjds,fibers)
             if len(fiber_item)>0:
                fiber_dict.update(fiber_item)
         tend=MPI.Wtime()
         #rank0 create all, then close an reopen.-Quincey Koziol 
         #define reduce operation
         counterop = MPI.Op.Create(add_dic, commute=True) 
         fiber_item_length=len(fiber_dict)
         fiber_dict_tmp=deepcopy(fiber_dict)
         global_fiber= comm.allreduce(fiber_dict_tmp, op=counterop)       
        treduce=MPI.Wtime()
        if rank==0:
         print ("Number of processes %d"%nproc)
         print ("length of global_fiber: %d"%(len(global_fiber)))
         #print ("parse csv time: %.2f"%(tstart-tstartcsv))
         print ("Get fiber metadata costs: %.2f"%(tend-tstart))
         print ("Allreduce dics costs: %.2f"%((treduce-tend)))
        
##_______________ Create File ______________##  
        if rank==0 and (template==1 or template==2):
           temp_start=MPI.Wtime()
           try:
            create_template(outfile,global_fiber,'fiber',rank)
#            catalog_number=count_unique(global_fiber) #(plates/mjd, num_fibers)
#            print ('number of unique fibers:%d '%len(catalog_number))           
#            catalog_types=get_catalogtypes(sample_file) # dict: meta, (type, shape)
#            global_catalog=(catalog_number,catalog_types)
#            create_template(outfile,global_catalog,'catalog',rank)
           except Exception as e:
            print("template creation error")
            traceback.print_exc()
            pass
           temp_end=MPI.Wtime()
           print ("Template creation time: %.2f"%(temp_end-temp_start))
        comm.Barrier() 
        tcreated=MPI.Wtime()
##_______________ Fiber sorting ______________##TODO: Check later IO 
        copy_global_catalog=global_fiber.copy() # shallow copy
        revised_dict=locate_fiber_in_catalog(copy_global_catalog)
        #now revised_dict has: p/m, fiber_id, infile, global_offset
        copy_revised_dict=revised_dict.items()
        total_unique_fiber=len(copy_revised_dict)
        #distribute the workload evenly to each process
        step=int(total_unique_fiber / nproc)+1
        rank_start =int( rank * step)
        rank_end = int(rank_start + step)
        if(rank==nproc-1):
         rank_end=total_unique_fiber # adjust the last rank's range
         if rank_start>total_unique_fiber:
            rank_start=total_unique_fiber
        catalog_dict=copy_revised_dict[rank_start:rank_end]
##__________________ I/O ___________________##
        if template ==0 or template==2: 
         try: 
          #collectively open file
          hx = h5py.File(outfile,'a',driver='mpio', comm=MPI.COMM_WORLD)
          hx.atomic=False 
         except Exception as e:
          traceback.print_exc()        
        topen=MPI.Wtime()
        tclose=topen
        
        if template==0 or template==2:
           fiber_copyts=MPI.Wtime()
           overwrite_template(hx,fiber_dict,'fiber')
#           overwrite_template(outfile,fiber_dict,'fiber')
           fiber_copyte=MPI.Wtime()
           #print ("rank:%d\tlength:%d\tcost:%.2f"%(rank,fiber_item_length,fiber_copyte-fiber_copyts))
#           #for each fiber, find the catalog, then copy it
#           catalog_copyts=MPI.Wtime()
#           overwrite_template(hx,catalog_dict,'catalog')
#           catalog_copyte=MPI.Wtime()
           comm.Barrier()
           tclose_s=MPI.Wtime()
           hx.close()
           tclose=MPI.Wtime()
        if rank==0:
           print ("Fiber copy: %.2f\nTotal Cost: %.2f"%(fiber_copyte-fiber_copyts,tclose-tstart))
           #print ("File open: %.2f\nFiber copy: %.2f\nFile close: %.2f\nTotal Cost: %.2f"%(topen-tcreated,fiber_copyte-fiber_copyts,tclose-tclose_s,tclose-tstart))
if __name__=='__main__': 
    parallel_select()
