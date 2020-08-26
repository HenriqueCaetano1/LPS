#!/usr/bin/env python
# coding: utf-8

# In[26]:


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
from itertools import combinations
import itertools

# In[27]:


xis = 1000
beta = [0,0.1,0.2,0.3,0.4]
alpha = [0,0.1,0.2,0.3,0.4]
r = [0.2,0.4,0.6,0.8,1]
n = [3,4,5,6]


# In[28]:


def remove_all_and_measure_capacities(G,beta):
    for z in ["Normal", "VNS"]:
        cap_list = []
        for k in range(100):
            cap_list.append([])
            rem.set_nodes_capacity(G,mean_node,std_node)
            rem.set_edges_flow(G,alpha)
            rem.set_nodes_maximum(G,carregamento)
            Active = rem.set_active_graph(G)
            Backup = rem.set_backup_graph(G,Active,1)
            Failure = rem.set_failure_graph()
            info = ut.pandas_print(Active)
            initial_capacity = round(sum(info['Capacity']),2)
            cap_list[k].append(100)
            total_nodes = len(Active.nodes())
            for i in (range(len(Active.nodes())-1)):
                #if z == "Intencional":
                    #rem.remove_highest_degree_node(G,Active,Backup,Failure)
                #else:
                    #rem.remove_random_node(G,Active,Backup,Failure)
                rem.remove_random_node(G,Active,Backup,Failure)
                info = ut.pandas_print(Active)
                cap_list[k].append(round(100*sum(info['Capacity']/initial_capacity),2))
        average = [0]*len(G.nodes())
        for i in range(len(cap_list)):
            for j in range(len(cap_list[i])):
                average[j] += cap_list[i][j]
        for k in range(len(average)):
            average[k]=round(average[k]/100,2)
        porcentagem = [round(100*(i/total_nodes),2) for i in range(total_nodes)]
        if z == "Normal":
            plt.plot(porcentagem,average,'o-',label = 'normal')
        else:
            plt.plot(porcentagem,average,'o-',label = 'Intencional')

    plt.xlabel("Numero de nos removidos",fontsize = 15)
    plt.ylabel("Capacidade total do grafo",fontsize = 15)
    plt.legend(loc=3, prop={'size': 13})
    plt.title("Progressao da capacidade - livre escala",fontsize = 15)
    plt.show()



'''def swap_k_edges(Active,Backup,Failure,k):
    for i in range(k):
        key = False
        while(not key):
            rem.remove_random_edge(Active,Backup,Failure)
            rem.activate_random_edge(Active,Backup,Failure)
            Active_edges_list = ut.unpack_list(Active.edges())
            Backup_edges_list = ut.unpack_list(Backup.edges())
            P_active = Active.copy()
            P_backup = Backup.copy()
            try:
                rem = random.choice(Active_edges_list)
                add = random.choice(Backup_edges_list)
                P_backup.add_edge(*rem,flow = P_active[rem[0]][rem[1]]['flow'])
                P_active.remove_edge(*rem)
                P_active.add_edge(*add,flow = P_backup[add[0]][add[1]]['flow'])
                P_backup.remove_edge(*add)
                if nx.is_connected(P_active):
                    key = True
                    Active = P_active
                    Backup = P_backup
                    #print('rem:{}, add:{}'.format(rem,add))
                else:
                    try:
                        Active_edges_list.remove(rem)
                        Backup_edges_list.remove(add)
                    except IndexError:
                        break

            except IndexError:
                pass

    return Active,Backup'''

def swap_k_edges(Active,Backup,Failure,k):
    for i in range(k):
        Active_edges_list = ut.unpack_list(Active.edges())
        Backup_edges_list = ut.unpack_list(Backup.edges())
        rem = random.choice(Active_edges_list)
        add = random.choice(Backup_edges_list)
        Backup.add_edge(*rem,flow = Active[rem[0]][rem[1]]['flow'])
        Active.remove_edge(*rem)
        Active.add_edge(*add,flow = Backup[add[0]][add[1]]['flow'])
        Backup.remove_edge(*add)
    return [Active,Backup]


def neighborhood_method(Graph,number):
    switcher = {
        #0:nx.average_shortest_path_length(Graph),
        0:st.mean(nx.betweenness_centrality(Graph).values()),
        #0:st.mean(nx.closeness_centrality(Graph).values()), #from 0 to 2: general graph functions, doesn't care about the graph parameters
        #0:nx.average_shortest_path_length(Graph,'flow'),
        #0:st.mean(nx.betweenness_centrality(Graph,weight='flow').values())
    }

    func = switcher.get(number)
    #print(func)
    return func

def vns_method(Active,Backup,Failure,j_max,vns_function,swap_number_max):
    std = {}
    new = {}
    S_active = Active.copy()
    S_backup = Backup.copy()
    S_failure = Failure.copy()
    j = 0
    inter_max = j_max/10
    inter = 0
    swap_number = 1
    std = neighborhood_method(Active,vns_function)
    while (j < j_max and inter < inter_max):
        S_active = Active.copy()
        S_backup = Backup.copy()
        S_failure = Failure.copy()
        [S_active,S_backup] = swap_k_edges(S_active,S_backup,S_failure,swap_number)
        new = neighborhood_method(S_active,vns_function)
        if new >= std:
            inter+=1
            if swap_number < swap_number_max:
                swap_number+=1
            else:
                swap_number = 1
        else:
            inter = 0
            swap_number = 1
            edge_set = ut.difference(Active,S_active)
            Active = S_active
            Backup = S_backup
            Failure = S_failure
            std = new
        #print(std)
        #print('new:{} std:{} number:{}'.format(new[number],std[number],number))
        #std[number] = new[number]
        j+=1
    return [Active,Backup,edge_set]

def graph_flow_comparison(G,Active,Backup,Failure,j_max,vns_function,swap_number):
    vns_measure = {}
    before_measure = {}
    change_measure =  {}
    b_overload = rem.total_overload(Active)
    before_measure = neighborhood_method(Active,vns_function)
    Active_temp = Active.copy()
    Backup_temp = Backup.copy()
    [Active_temp,Backup_temp] = rem.graph_flow(G,Active_temp,Backup_temp)
    normal_overload = rem.total_overload(Active_temp)
    [Active_vns,Backup_vns,edge_set] = vns_method(Active,Backup,Failure,j_max,n_hoods,swap_number)
    vns_measure = neighborhood_method(Active_vns,vns_function)
    [Active_vns,Backup_vns] = rem.graph_flow(G,Active_vns,Backup_vns)
    vns_overload = rem.total_overload(Active_vns)
    try:
        normal_overload_change = 100*round((b_overload - normal_overload)/b_overload,4)
    except ZeroDivisionError:
        normal_overload_change = 0
    try:
        vns_overload_change = 100*round((b_overload - vns_overload)/b_overload,4)
    except ZeroDivisionError:
        vns_overload_change = 0
    try:
        change_measure[i] = 100*round((vns_measure - before_measure)/before_measure,4)
    except ZeroDivisionError:
        change_measure[i] = 0
    return [normal_overload_change,vns_overload_change,change_measure,edge_set]

def remove_highest_flow_edge(G,Active,Backup,Failure):
    Total = rem.set_total_graph(Active, Backup)
    list = sorted(Total.edges(data=True), key=lambda t: t[2].get('weight', 1))
    x = [list[0][0],list[0][1]]
    if x in Backup.edges():
        Failure.add_edge(*x,flow = Backup[x[0]][x[1]]['flow'])
        Backup.remove_edge(*x)
    if x in Active.edges():
        Failure.add_edge(*x,flow = Active[x[0]][x[1]]['flow'])
        Active.remove_edge(*x)
    Failure.nodes[x[0]]['capacity'] = 0
    Failure.nodes[x[1]]['capacity'] = 0


'''graph_flow_comparison(G,Active,Backup,Failure,k_iter,k_break,n_hoods)'''


#graph_flow_comparison chama vns_method chama swap_k_edges
