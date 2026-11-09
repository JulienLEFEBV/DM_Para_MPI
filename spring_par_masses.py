#! /usr/bin/env python3

import numpy as np
import time
import sys

from spring_lib import *

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

try:
    display = not '-nodisplay' in sys.argv
    nb_masses = int(sys.argv[1])
    nb_springs = int(sys.argv[2])
    nb_turns = int(sys.argv[3])
except:
    print(f'Usage {sys.argv[0]} nb_masses nb_strings nb_turns [-nodisplay]')
    sys.exit(0)

if rank == 0:
    masses, springs = generate_springs(nb_masses, nb_springs)
else : 
    masses, springs = None,None

comm.barrier()
time_start = time.time()
nb_interaction = np.zeros(1,dtype='i')

masses_local = np.empty((nb_masses//size,6),dtype='i')
forces_local = np.empty((nb_masses//size,2),dtype='i')

for _ in range(nb_turns):
    #Calcul des forces exercées les différentes masses non parallelisable en divisant le tableau des masses
    if rank == 0 : 
        forces = np.zeros((nb_masses,2),dtype='i')
        for s in springs:
            id_masse_i = s[IDA]
            id_masse_j = s[IDB]
            F = interaction(s,masses)
            nb_interaction[0]+=1
            forces[id_masse_i] += F
            forces[id_masse_j] -= F
    else :
        forces = None
    #Mise à jour des positions parallelisable en divisant le tableau des masses
    comm.Scatter(masses,masses_local,root=0)
    comm.Scatter(forces,forces_local,root=0)
    for i in range(len(masses_local)):
        update(masses_local, i, forces_local[i])
    #Affichage
    comm.Gather(masses_local,masses,root=0)
    if display and rank == 0:
        display_plot(masses, springs)


delta_time = time.time() - time_start

# all_interactions should contain the number of calls of interaction function on all processes
if rank == 0 :
    all_interactions = np.zeros(size,dtype='i')
else : 
    all_interactions = None
comm.Gather(nb_interaction,all_interactions,root=0)
if rank == 0:
    total_interaction = sum(all_interactions)
    max_interaction = max(all_interactions)
    min_interaction = min(all_interactions)
    unbalance = max_interaction-min_interaction

    print('Duration:', delta_time)
    print('Signature:', signature(masses))
    print('Interactions:', total_interaction)
    print('Unbalance:', unbalance)
