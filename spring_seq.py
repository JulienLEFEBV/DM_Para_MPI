#! /usr/bin/env python3

import numpy as np
import time
import sys

from spring_lib import *

try:
    display = not '-nodisplay' in sys.argv
    nb_masses = int(sys.argv[1])
    nb_springs = int(sys.argv[2])
    nb_turns = int(sys.argv[3])
except:
    print(f'Usage {sys.argv[0]} nb_masses nb_strings nb_turns [-nodisplay]')
    sys.exit(0)


masses, springs = generate_springs(nb_masses, nb_springs)

time_start = time.time()
nb_interaction = 0

for _ in range(nb_turns):
    #Calcul des forces exercées les différentes masses
    forces = np.zeros((nb_masses,2))
    for s in springs:
        id_masse_i = s[IDA]
        id_masse_j = s[IDB]
        F = interaction(s,masses)
        nb_interaction += 1
        forces[id_masse_i] += F
        forces[id_masse_j] -= F
    #Mise à jour des positions
    for i in range(nb_masses):
        update(masses, i, forces[i])
    #Affichage
    if display:
        display_plot(masses, springs)


delta_time = time.time() - time_start

# all_interactions should contain the number of calls of interaction function on all processes
all_interactions = [nb_interaction]
total_interaction = sum(all_interactions)
max_interaction = max(all_interactions)
min_interaction = min(all_interactions)
unbalance = max_interaction-min_interaction

print('Duration:', delta_time)
print('Signature:', signature(masses))
print('Interactions:', total_interaction)
print('Unbalance:', unbalance)
