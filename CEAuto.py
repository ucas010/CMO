#!/usr/bin/env python

from __future__ import division
from __future__ import unicode_literals

__author__ = 'Bin Ouyang & Fengyu_xie'
__version__ = 'Dev'


import os
import sys
import argparse
import json
import time
from pymatgen.io.cif import CifParser
from monty.json import MSONable

from generator_tools,analyzer_tools,runner_tools,gs_tools import *

###################################
#One example of OXRange we use is given below:
#ox_ranges = {'Mn': {(0.5, 1.5): 2,
#            (1.5, 2.5): 3,
#            (2.5, 3.4): 4,
#            (3.4, 4.05): 3,
#            (4.05, 5.0): 2}};
#The way it works is really emperical but we did not find a generalized way to
#correlate charge states with magnetism. Maybe we can automate a self consistent routine
#to check the check balance during VASP caculation loading and pick a best one. Or just 
#Pre-calculate it and make it into a data file like json or yaml (works like the DFT+U paprameters);
##################################

class CEAutojob(MSONable):
    """
        An abstract Cluster Expansion automated step. Can be constructed by specifiying job type and reading setting.mson file. 
        Has 4 different steps:
        1, generator: enumerate structures, do sampling, and update vasp calculation folder. writes a prim file.
        2, analyzer: read, analyze vasp calculation results, updates ce.mson and calcdata.mson.
        3, runner: submit calculations to ginar, and keep logging of the calculational status.
        4, gs_solver: find ground state, add gs into vasp_dir, fire a calculation. Call analyzer after success.

        The CE improvement sequence should be:
        generator(cycle 1):N structures -> runner -> analyzer -> gs_solver: N_hull structures -> runner -> analyzer -> RMSE and 
        termination conditions -> generator(cycle 2)

        Runner is the pivot. Still looking at it. Using old stuff as alternative.
    """
    def __init__(self):
        raise NotImplementedError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--fit', help="Fit CE based on VASP outputs", action='store_true')
    
    parser.add_argument('-g','--generate', help="Generate MC structures from this CE", action='store_true')
    parser.add_argument('--prim', help="cif file of primitive cell to construct the CE work from", type=str, default='prim.cif')
    parser.add_argument('--numsc',help="Number of skewed and unskewed supercells to sample",type=int,default=10)
    parser.add_argument('--transmat',help="Transformation matrix to prim, if it is possible to make your prim more symmetric.\                        Example: --transmat = '[[1,0,0],[0,1,0],[0,0,1]]' ", type=str, default=None)
    parser.add_argument('--compaxis',help="Axis on which you want to decompose your compositions.\ 
                         Example:--compaxis='LiCoO2,LiF,CoO'",type=str, default=None)
    parser.add_argument('--enforceoccu',help='''Minimum required occupation fraction for each site. Site refered to by
                      index. Example: --enforceoccu='[0.0,1.0,1.0,1.0]'. ''',type=str,default=None)
    parser.add_argument('--samplestep',help="Sampling step of number of species occupying sublattice sites.",type=int,default=1)
    parser.add_argument('--scs', help="Max supercell matrix determinant to be enumerated (must be integer)",type=int,default=64)
    parser.add_argument('--cefile',help="Read and use a existing CE file.",default='')
     
    parser.add_argument('-s','--solveGS',help="Solve for ground state with current CE", action='store_true')
    parser.add_argument('-r','--run',help="Submit vasp jobs for VASP directory", action='store_true')

    parser.add_argument('--vasprun',help="Store all vasp running data under this directory.",type=str,default='vasp_run')

    args = parser.parse_args()
    import time

    start_time = time.time()
    
    if args.generate:
        if os.path.isfile('generator.mson'):
            print("Using existing generator setup.")
            with open('generator.mson','r') as generatorfile:
            generator = StructureGenerator.from_dict(json.load(generatorfile))
        else:
            print("Constructing new generator.")
            prim = CifParser(args.prim).get_structures()[0]
            compaxis = json.loads(args.compaxis) if args.compaxis else None
            enforceoccu = json.loads(args.enforceoccu) if args.compaxis else None
            transmat = json.loads(args.transmat) if args.transmat else None

            generator = StructureGenerator(prim, args.vasprun, enforceoccu, args.samplestep, args.scs,args.numsc,compaxis,transmat)

    print("--- %s seconds ---" % (time.time() - start_time)) 
