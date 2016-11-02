# H5Boss
Exploratory tools for managing BOSS spectra. 

Boss is originally maintained as millions of fits file in thousands of different folders. Accessing and analyzing them are inefficient in terms of I/O bandwidth and programming productivity. In h5boss, we focus on:

1. Reformatting: Preserve the fits file structure and specture hierarchicy using HDF5
2. Object I/O: Design object interface for accessing the files as pmf indexed object
3. Query Caching: Develop transparent cache for restoring analysis workflow and reducing metadata overhead
4. Subset Selection: Support subset selection, moving various interested fiber object and catalog together and save in one file
4. Data mover: Design API for moving data through various storage tiers. 

Currently, h5boss is implemented in both python and c version, in which the python version is actively maintained and supported. The c version is mainly for I/O sensitive users/applications. 

#Demo with h5boss_py
1. source cori-setup
2. cd h5boss_py/demo
2. subset -h
3. add -h
4. update -h

#Demo with h5boss_c
1. cd h5boss_c
2. make 
