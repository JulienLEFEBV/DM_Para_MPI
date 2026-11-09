

= Compte Rendu DM

== Question 5 :

=== Programme _spring_par_masses.py_ : 

Partager le tableau masses nous permet de paralléliser facilement la partie des mise à jours. Cependant comme nous ne partageons que le tableau _masses_ entre les différents processus nous ne pouvons pas paralléliser la partie du calcul des intéractions. En effet elle se fait en parcourant le tableau _springs_ donc nous ne pouvons pas paralléliser cette partie du code à moins de parcourir le tableau _springs_ pour trouver toute les apparition de chaque masses à chaque extrémités des ressorts ce qui serait inefficace. Cela nous donne donc un code mal équilibrer dans les appels à la fonction _interaction_ et beaucoup de processus en attente.

=== Programme _spring_par_springs.py_ :

Partager le tableau _springs_ nous permet de paralléliser la partie du calcul des interactions. Cependant nous ne pouvons pas facilement paralléliser la partie des mises à jour de la position des masses, comme celle-ci se fait par un parcours du tableau _masses_. Nous sommes aussi obligés de donner le tableau _masses_ complet à tous les processus, or celui-ci peut avoir une taille importante sur certains grands problèmes.

=== Programme _spring_par_both.py_ : 

Partager les deux tableaux _springs_ et _masses_ entre les différents processus nous permet de paralléliser facilement la partie de calcul des interactions mais aussi la partie des mises à jour des positions des différentes masses. Cependant cela nous donne un code avec beaucoup de synchronisation entre les différents processus par de nombreux appels aux fonctions de MPI ce qui diminue l'efficacité de notre programme. Nous avons aussi le même problème que précédemment dans _spring_par_springs.py_ avec le tableau _masses_ qui doit être donner à tous les processus.

=== Programme _spring_par_opti.py_ :

Pour optimiser le programme nous pouvons faire en sorte de donner à chaque processus uniquement les masses dont il a besoin pour le calcul des intéractions avec les différents ressorts. Ainsi nous pouvons effectuer uniquement la mise à jour des nouvelles positions des masses utilies à chaque processus dans chaque processus. Cela permet de limiter le problème de la redondance des calculs vu dans le programme _spring_par_springs_ et de limiter celui du nombre de communication vu dans le programme _spring_par_both_. Et cela limite aussi le problème de devoir partager le tableau _masses_ en entier entre chaque processus alors que celui-ci peu être conséquent.

#pagebreak()
== Question 6

=== Resultats pour les paramètres 12 12 1 :

```
Duration
nbhosts                                                       
1        0.000172    0.000214     0.000206  0.000215  0.000419
2        0.000163    0.000246     0.000206  0.000181  0.000380
3        0.000161    0.000238     0.000192  0.000180  0.000372
4        0.000167    0.000201     0.000232  0.000173  0.000394

Interactions
nbhosts                                                  
1         12          12           12        12        12
2         12          12           12        12        12
3         12          12           12        12        12
4         12          12           12        12        12

Unbalance
nbhosts                                                  
1          0           0            0         0         0
2          0          12            0         0         0
3          0          12            0         0         0
4          0          12            0         0         0

Maximal final grading 20/20
Depending on the actual code, this value is the maximal grade you can have
```

=== Resultats pour les paramètres 240 -1 100:

```
Duration
               seq  par_masses  par_springs   par_both   par_opti
nbhosts                                                          
1        11.549585   10.489707    10.389420  10.511301  10.569989
2        11.515933   10.614316     5.317981   5.285021   5.392213
3        11.627599   11.197727     3.771777   3.676479   3.797384
4        11.322958   11.294819     2.854998   2.823319   2.941301

Interactions
             seq  par_masses  par_springs  par_both  par_opti
nbhosts                                                      
1        2868000     2868000      2868000   2868000   2868000
2        2868000     2868000      2868000   2868000   2868000
3        2868000     2868000      2868000   2868000   2868000
4        2868000     2868000      2868000   2868000   2868000

Unbalance
         seq  par_masses  par_springs  par_both  par_opti
nbhosts                                                  
1          0           0            0         0         0
2          0     2868000            0         0         0
3          0     2868000            0         0         0
4          0     2868000            0         0         0

Maximal final grading 20/20
Depending on the actual code, this value is the maximal grade you can have
```

=== Resultat pour les paramètres 300 20100 20:
```
Duration
              seq  par_masses  par_springs  par_both  par_opti
nbhosts                                                       
1        1.639150    1.474081     1.501576  1.489783  1.522653
2        1.600219    1.512500     0.763026  0.746679  0.792432
3        1.609348    1.560985     0.530255  0.516067  0.562937
4        1.618447    1.570105     0.407654  0.387601  0.445652

Interactions
            seq  par_masses  par_springs  par_both  par_opti
nbhosts                                                     
1        402000      402000       402000    402000    402000
2        402000      402000       402000    402000    402000
3        402000      402000       402000    402000    402000
4        402000      402000       402000    402000    402000

Unbalance
         seq  par_masses  par_springs  par_both  par_opti
nbhosts                                                  
1          0           0            0         0         0
2          0      402000            0         0         0
3          0      402000            0         0         0
4          0      402000            0         0         0

Maximal final grading 20/20
Depending on the actual code, this value is the maximal grade you can have
```

=== Conclusion :

Nous pouvons voir que la version séquentielle et la version _spring_par_masses.py_ sont les plus inefficaces, ce qui est cohérent puisque la version séquentielle ne profite pas du parallélisme et parce que la version _spring_par_masses.py_ est très déséquilibrée sur ses appels à la fonction _interaction_ entre les différents processus. 

Nous pouvons aussi voir que la version _spring_par_opti.py_ est moins efficace que les versions _spring_par_both.py_ et _spring_par_springs.py_ sur le petit problème de paramètres 12 12 1, ce qui est cohérent du fait qu'elle possède un temps de prétraitement plus important que nous ne rentabilisons pas puisque nous n'effectuons qu'une seule itération. Cependant elle devient à peu près aussi efficace que les deux autres sur les problèmes plus gros. De plus, même si cela ne se voit pas avec les tests proposés, la version optimisée est la plus robuste sur les grands problèmes. En effet, la version _spring_par_both.py_ a un temps d'exécution plus long sur les problèmes avec beaucoup de masses et peu de ressorts et la version _spring_par_springs.py_ a un temps d'exécution beaucoup plus grand sur les problèmes avec beaucoup de masses et de ressorts alors que la version optimisée donne un résultat satisfaisant pour tous les problèmes.
