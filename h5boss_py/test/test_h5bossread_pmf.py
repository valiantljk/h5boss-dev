from __future__ import division, print_function
import numpy as np
import h5py
import sys
sys.path.append('/global/homes/j/jialin/.local/edison/2.7-anaconda/lib/python2.7/site-packages')
import time
import fitsio
import traceback
import optparse
import argparse
import pandas as pd
fitserr=0
coaderr=0
boss_dir="/global/projecta/projectdirs/sdss/data/sdss/dr12/boss/spectro/redux/v5_7_0/"
h5boss_dir="/global/cscratch1/sd/jialin/h5boss/"
i_wave={"flux": 1,"ivar": 0,"andmask": 2, "ormask": 3, "wavedisp": 4, "sky": 6} # digit is the HDU number
h5b_wave={'WAVE', 'FLUX', 'IVAR', 'AND_MASK', 'OR_MASK', 'WAVEDISP', 'SKY', 'MODEL'} # dx.dtype.names
def parsePMF(pmflist):
    try:
        df = pd.read_csv(pmflist,delimiter=' ',names=["plates","mjds","fibers"],index_col=None,dtype=str,header=0)
        df = df.sort_values(by="plates",ascending=[1])
        plates = list(map(str,df['plates'].values))
        mjds = list(map(str,df['mjds'].values))
        fibers = list(map(str,df['fibers'].values))
    except Exception as e:
        print("pmf csv read error or not exist:%s"%e,pmflist)
        print("e.g., 1st row of csv should be 'plates mjds fibers'")
    return (plates,mjds,fibers)

def h5bread_s_pmf(fx,plate,mjd,fiber,wave):
    '''
       read the pmf from pre-selected hdf5 file
       
    '''
    global fitserr, coaderr
    dwave=0
    pmfcad=plate+"/"+mjd+"/"+fiber+"/coadd"
    try:
     if pmfcad in fx.keys():
       dwave=fx[pmfcad][wave]
     else:
       print ("pmfcad %s not found in pre file"%(pmfcad,fx))
    except Exception as e:
      coaderr=coaderr+1
    return dwave

def h5bread_pmf(plate,mjd,fiber,wave):
    '''
        read the pmf from source hdf5 files, to have an apple2apple comparison with fitsread_pmf
        para: plate, mjd, fiber
        para: wave is the name of wavelength variable
        return: fiber-th row in dataset wave
    '''
    dwave=0
    global fitserr, coaderr
    try:
        h5bfile=h5boss_dir+plate+"-"+mjd+".hdf5"
        dh5=h5py.File(h5bfile,'r')
    except Exception as e:
        #traceback.print_exc()
        fitserr=fitserr+1
        #print("fits open error %s"%h5bfile)
        pass
        #pass 
    try:
        #print ("%s-%s,%s,fiber %s"%(plate,mjd,wave,fiber))
        pmfcad=plate+"/"+mjd+"/"+fiber+"/coadd"
        dwave=dh5[pmfcad][wave] # only access one wavelength, i.e., 1 column 
    except Exception as e:
        #traceback.print_exc()
        #print("extraction error %s-%s %s"%(plate,mjd,fiber))
        coaderr=coaderr+1
        pass
    return dwave


def test_h5bread_pmf(pmflist,var):
    try:
        (plate,mjd,fiber)=parsePMF(pmflist)
    except Exception as e:
        traceback.print_exc()
        print("parse pmf: %s error"%pmflist)
    print ("reading %d pmf"%len(plate))
    st=time.time()
    try:
        for i in range(0,len(plate)):
            h5bread_pmf(plate[i],mjd[i],fiber[i],var)
    except Exception as e:
        #traceback.print_exc()
        #print("read fiber %s error %s"%(fiber[i],var))
        pass
    print ("h5boss:%.2f seconds"%(time.time()-st))
    global fitserr, coaderr
    print ("hdfserr %d, coaderr %d"%(fitserr,coaderr))
def test_h5bread_s_pmf(pmflist,var,pre):
    try:
        (plate,mjd,fiber)=parsePMF(pmflist)
    except Exception as e:
        traceback.print_exc()
        print("parse pmf: %s error"%pmflist)
    print ("reading %d pmf"%len(plate))
    st=time.time()
    try:
 	fx=h5py.File(pre,'r')
    except Exception as e:
        print("pre file open error %s"%pre)
        sys.exit()
    try:
        for i in range(0,len(plate)):
            h5bread_s_pmf(fx,plate[i],mjd[i],fiber[i],var)
    except Exception as e:
        #traceback.print_exc()
        print("read fiber %s error %s"%(fiber[i],var))
    try:
        fx.close()
    except Exception as e:
        print("pre file close error")
    print ("h5boss:%.2f seconds"%(time.time()-st))
    global fitserr, coaderr
    print ("hdfserr %d, coaderr %d"%(fitserr,coaderr))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='h5bread')
    parser.add_argument("pmf",    help="Plate/mjd/fiber list in csv")
    parser.add_argument("var",    help="Wavelength name: WAVE,FLUX,IVAR,AND_MASK,OR_MASK,WAVEDISP,SKY,MODEL")
    parser.add_argument("pre",	  help="pre-selected h5boss file: filename or none")
    opts=parser.parse_args()
    pmflist = opts.pmf
    var = opts.var
    pre = opts.pre
    if pre == 'none':
       print ("read from source files")
       test_h5bread_pmf(pmflist,var)
    else: 
       print ("read from pre-selected file %s"%pre)
       test_h5read_s_pmf(pmflist,var,pre) 
