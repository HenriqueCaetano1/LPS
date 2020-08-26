# -*- coding: utf-8 -*-
from __future__ import division
import networkx as nx
import random
import utils as ut
import statistics as st
import removal_and_reconfiguration_functions as rem
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import collections
import math

xis = 2000
beta = [0,0.1,0.2,0.3,0.4]
alpha = [0,0.1,0.2,0.3,0.4]
r = [0.2,0.4,0.6,0.8,1]
n = [3,4,5,6]

def remove_all_and_measure_capacities(G,beta):
    for z in ["Aleatório", "Intencional"]:
        cap_list = []
        for k in range(100):
            print(k)
            cap_list.append([])
            rem.set_nodes_capacity(G,50,5)
            rem.set_nodes_maximum_capacity(G,0.5)
            rem.set_edges_flow(G,5)
            Active = rem.set_active_graph(G)
            Backup = rem.set_backup_graph(G,Active,1)
            Failure = rem.set_failure_graph()
            info = ut.pandas_print(Active)
            initial_capacity = round(sum(info['Capacity']),2)
            cap_list[k].append(100)
            total_nodes = len(Active.nodes())
            for i in (range(len(Active.nodes())-1)):
                if z == "Aleatório":
                    rem.remove_highest_degree_node(G,Active,Backup,Failure)
                else:
                    rem.remove_random_node(G,Active,Backup,Failure)
                info = ut.pandas_print(Active)
                cap_list[k].append(round(100*sum(info['Capacity']/initial_capacity),2))
        average = [0]*len(G.nodes())
        for i in range(len(cap_list)):
            for j in range(len(cap_list[i])):
                average[j] += cap_list[i][j]
        for k in range(len(average)):
            average[k]=round(average[k]/100,2)
        print(len(cap_list))
        print(len(cap_list[0]))
        print("Media:{}".format(average))
        print(len(average))
        porcentagem = [round(100*(i/total_nodes),2) for i in range(total_nodes)]
        if z == "Aleatório":
            plt.plot(porcentagem,average,'o-',label = 'Aleatorio')
        else:
            plt.plot(porcentagem,average,'o-',label = 'Intencional')

    plt.xlabel("Numero de nos removidos",fontsize = 20)
    plt.ylabel("Capacidade total do grafo",fontsize = 20)
    plt.legend(loc=3, prop={'size': 15})
    plt.tight_layout()
    plt.show()
total = [[],[],[],[]]
def remove_all_nodes_andcheck_25_50_75(n):
    for z in n:
        rem25,rem50,rem75 = [],[],[]
        for j in range(100):
            G = nx.grid_2d_graph(n,n)
            rem.set_nodes_capacity(G,50,5)
            rem.set_nodes_maximum_capacity(G,0.5)
            rem.set_edges_flow(G,1.5)
            Active = rem.set_active_graph(G)
            Backup = rem.set_backup_graph(G,Active,0.5)
            Failure = rem.set_failure_graph()
            Initial = Active.copy()
            flag25,flag50,flag75 = False,False,False
            rem25.append(100)
            rem50.append(100)
            rem75.append(100)
            for i in (range(len(Active.nodes())-1)):
                rem.remove_random_node(G,Active,Backup,Failure)
                list = rem.check_capacity_decrease(Active,Initial)
                if list[2] != 0 and flag25 == False:
                    rem25[j] = list[2]
                    flag25 = True
                elif list[1] != 0 and flag50 == False:
                    rem50[j] = list[1]
                    flag50 = True
                elif list[0] != 0 and flag75 == False:
                    rem75[j] = list[0]
                    flag75 = True
            print("25: {},50:{},75:{}".format(rem25[j],rem50[j],rem75[j]))
        total25 = round(st.mean(rem25),2)
        total50 = round(st.mean(rem50),2)
        total75 = round(st.mean(rem75),2)
        total[0].append(z)
        total[1].append(total25)
        total[2].append(total50)
        total[3].append(total75)
    info = pd.DataFrame({'Graph Nodes':total[0],'25% removed':total[1],'50% removed':total[2],'75% removed':total[3]})
    return info
'''G = nx.grid_2d_graph(6,6)
rem.set_nodes_capacity(G,50,10)
rem.set_nodes_maximum_capacity(G,0.5)
rem.set_edges_flow(G,5)
Active = rem.set_active_graph(G)
Backup = rem.set_backup_graph(G,Active,0.5)
Failure = rem.set_failure_graph()
ut.pandas_print(G)
rem.graph_flow(G,Backup,Active)
ut.pandas_print(G)'''

G = nx.scale_free_graph(100)
H = rem.create_directed_graph(G)
remove_all_and_measure_capacities(H,beta)
