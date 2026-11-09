#! /usr/bin/env python3

import numpy as np
import time
import sys

from spring_lib import *

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

infini_negatif = np.iinfo(np.int32).min

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
    masses, springs = np.empty((nb_masses,6),dtype='i'),None

comm.barrier()
time_start = time.time()
nb_interaction = np.zeros(1,dtype='i')

nb_springs = nb_springs if nb_springs!=-1 else nb_masses*(nb_masses-1)//2

#Prétraitements
if rank==0 :
    masses_utiles = np.empty((2*nb_springs,6),dtype='i') #masses_utiles contient les masses qu'il faut distribuer au autre processus en fonction de leurs ressorts
    est_utile_masse = np.zeros(nb_masses) #ce tableau permet de trouver les indices des masses fixes  
    for i,s in enumerate(springs):
        idA = s[IDA]
        idB = s[IDB]
        masses_utiles[2*i]=masses[idA]
        masses_utiles[2*i+1]=masses[idB]
        est_utile_masse[idA] = 1
        est_utile_masse[idB] = 1
else :
    masses_utiles = None

springs_local = np.empty((nb_springs//size,4),dtype='i')
comm.Scatter(springs,springs_local,root=0)

forces = np.zeros((nb_masses,2),dtype='i')

masses_utiles_local = np.empty(((2*nb_springs)//size,6),dtype='i')
comm.Scatter(masses_utiles, masses_utiles_local,root=0)
masses_utiles_local = np.unique(masses_utiles_local,axis=0)

masses_loc = np.zeros((nb_masses,6),dtype='i') #Tableau permetant les appels à la fonction interaction et contenant une partie du résultat final
masses_loc.fill(infini_negatif) #Utile pour ne pas conserver les valeur non calculé lors du reduce du processus 0
indices = []

for ele in masses_utiles_local:
    masses_loc[ele[ID]]=ele
    indices.append(ele[ID])

if rank == 0 :
    for i in np.where(est_utile_masse==0):
        masses_loc[i]=masses[i]

for l in range(nb_turns):
    # Calcul des forces exercées les différentes masses parallelisable en divisant le tableau des springs 
    forces_local = np.zeros((nb_masses,2),dtype='i')
    for ele in springs_local:
       id_masse_i = ele[IDA]
       id_masse_j = ele[IDB]
       F = interaction(ele,masses_loc)
       nb_interaction[0]+=1
       forces_local[id_masse_i] += F
       forces_local[id_masse_j] -= F
    #Mise à jour des positions
    comm.Allreduce(forces_local,forces,MPI.SUM)
    for i in indices:
        update(masses_loc, i, forces[i])
    #Affichage
    if display:
        comm.Reduce(masses_loc,masses,MPI.MAX,root=0) 
        if rank==0:
            display_plot(masses, springs)

comm.Reduce(masses_loc,masses,MPI.MAX,root=0)

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
