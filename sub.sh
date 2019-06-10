#!/bin/bash
#$ -cwd
#$ -j y
#$ -N CMO_CE
#$ -m es
#$ -V
#$ -pe impi 16
#$ -o ll_out
#$ -e ll_er
#$ -S /bin/bash

mpiexec.hydra -n $NSLOTS pvasp.5.4.4.intel >> vasp.out 
