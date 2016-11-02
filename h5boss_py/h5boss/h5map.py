import numpy as np
import h5py
import time
import sys
import os
import csv
import traceback
from collections import defaultdict
fx=""
pid=""
inputfile=""
fiberdatalink={}
cataloglink={}
meta=['plugmap', 'zbest', 'zline',
                        'photo/match', 'photo/matchflux', 'photo/matchpos']

def _traverse_fibernode(name):
    '''
       para   : node name in a hdf5 group
       purpose: Find a dataset node, which should be an endpoint in its group hierarchy
unique_datsetpath datasettype datasetshape filepath plate mjd fiber
       return : (key,value)->(path_to_dataset, (dataset type, shape, filename, plate, mjd, fiber)) 
    '''
    global fx,pid,fiberdatalink,inputfile
    try:
     cur_node=name.encode('ascii','ignore')
     node=pid+'/'+cur_node
     p=pid.split('/')[0]
     m=pid.split('/')[1]
     f=pid.split('/')[2]
     node_t=str(type(fx[node]))
     if 'dataset' in node_t:
        node_t=fx[node].dtype
        node_sp=fx[node].shape
        fiberdatalink[node]=(node_t,node_sp,inputfile,p,m,f)
    except Exception as e:
     traceback.print_exc()
     pass
#node_type is used in ../script/subset_mpi.py, which is to create single shared file 
def map_fiber(infile):
        '''
           para  : filename, plate, mjd, fiber
           return: (key, value)->(datapath, (dtype, shape, filename, plate, mjd, fiber))
           python dict's updating can ensure that the key is unique, i.e., datapath: plate/mjd/fiber/../dataset is unique
        '''
        global pid,fiberdatalink, cataloglink, fx, inputfile
        inputfile=infile
        try:
         fx = h5py.File(infile, mode='r')
         for plate in fx.keys():
            for mjd in fx[plate].keys():
               spid= '{}/{}'.format(plate, mjd)
               for fib in fx[spid].keys():
                   if (fib.isdigit()):
                    pid = '{}/{}/{}'.format(plate, mjd, fib)
                    fx[pid].visit(_traverse_fibernode)
                #for im in meta:
                #  mnode=spid+'/'+im
                #  mnode_t=fx[mnode].dtype
                #  mnode_sp=fx[mnode].shape
                #  fiberdatalink[mnode]=(mnode_t,mnode_sp,infile)
         fx.close()
        except Exception as e:
         print (pid)
         traceback.print_exc()
         print (pid,infile)
         pass
        return (fiberdatalink)
def map_pmf(infile):
        '''
           para  : filename, plate, mjd, fiber
           return: (key, value)->(plates/mjd/fiber/, filename)
           python dict's updating can ensure that the key is unique, i.e., plate/mjd/fiber/../dataset is unique
        '''
        pmf={}
        try:
         fx = h5py.File(infile, mode='r')
         for plate in fx.keys():
            for mjd in fx[plate].keys():
               spid= '{}/{}'.format(plate, mjd)
               for fib in fx[spid].keys():
                   if fib.isdigit():
                    pid = '{}/{}/{}'.format(plate, mjd, fib)
                    pmf[pid]=infile 
         fx.close()
        except Exception as e:
         print (pid)
         traceback.print_exc()
         print (pid,infile)
         pass
        return (pmf)
def type_map(infile):
    '''
       para  : filename
       return: type and shape for each object, returned as tuple, dmap[0] is coadds, dmap[1] is exposure
       plate/mjd/coadds: 8 datasets
       plate/mjd/exposure/exposureid/b(r): 8 datasets
       # (key, value)->(plates/mjd/, (filename, fiberlist, fiberoffsetlist))   
    '''
    coadds_map={}
    exposures_map={}
    with h5py.File(infile,'r') as fx:
        try:
            p=fx.keys()[0]
            m=fx[p].keys()[0]
            pm=p+'/'+m
            coad_name=pm+'/coadds'
            expo_name=pm+'/exposures'
            coad=fx[coad_name].keys()
            subexpo_name=expo_name+'/'+fx[expo_name].keys()[0]+'/b'
            expo=fx[subexpo_name].keys()
            for icoad in coad:
                try:
                    icoad_name=coad_name+'/'+icoad
                    coadds_map[icoad]=(fx[icoad_name].dtype,fx[icoad_name].shape)
                except Exception as e:
                    print (icoad)
            for iexpo in expo:
                try:
                    iexpo_name=subexpo_name+'/'+iexpo
                    exposures_map[iexpo]=(fx[iexpo_name].dtype,fx[iexpo_name].shape)
                except Exception as e:
                    print (iexpo)
        except Exception as e:
            print (infile)
            traceback.print_exc()
    dmap=(coadds_map,exposures_map)
    return dmap

def coadd_map(fname_list):
    coadmap={}
    for ifile in fname_list:
     try:
      f=h5py.File(ifile,'r')
      p=f.keys()[0]
      m=f[p].keys()[0]
      pm=p+'/'+m
      pmc=pm+'/coadds'
      dsets=f[pmc].keys()
      if dsets[0]!='wave':
       dsize=f[pmc+'/'+dsets[0]].shape[1]
      else:
       dsize=f[pmc+'/'+dsets[1]].shape[0]
      coadmap[pm]=dsize
     except Exception as e: 
       pass
    return coadmap 
