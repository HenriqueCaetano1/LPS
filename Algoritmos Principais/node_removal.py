#!/usr/bin/env python
# coding: utf-8

from __future__ import division
import removal_and_reconfiguration_functions as rem
import matplotlib.pyplot as plt
import networkx as nx
import VNS as vns
import pandas as pd
import statistics as st

graph_size = 100 #posteriormente fazer com 600, 3000 e 30000 nos
beta = 0.95
alpha = 2
r = 1 #redundancia
j_max = 700 #numero maximo de execucoes do metodo VNS
n_hoods = 0 #numero de vizinhancas a ser utilizado
swap_number = 3 #numero de trocas de arestas máximas (vizinhancas) a serem feitas
iter_metodo = 100

cap_list_normal = []
cap_list_vns = []
cap_list_diff = []
edge_set_list = [[],[]]

data_node = pd.read_csv('dados70barras_node.csv')
data_edge = pd.read_csv('dados70barras_edge.csv')

mean_edge = data_edge['potencia'].mean()
std_edge = data_edge['potencia'].std()
mean_node = data_node['potencia_no'].mean()
std_node = data_node['potencia_no'].std()

for i in range(iter_metodo):
    print(i)
    cap_list_normal.append([])
    cap_list_vns.append([])
    cap_list_diff.append([])
    #G = rem.create_directed_graph(nx.watts_strogatz_graph(graph_size,int(round(6)),0.5))
    G = rem.create_directed_graph(nx.scale_free_graph(graph_size))
    #G = nx.grid_2d_graph(graph_size,graph_size)
    #G = Grafo_londrina
    rem.set_nodes_capacity(G,50,5)
    rem.set_edges_flow(G,alpha)
    rem.set_nodes_maximum(G,beta)
    Active_normal = rem.set_active_graph(G)
    Backup_normal = rem.set_backup_graph(G,Active_normal,r)
    Failure = rem.set_failure_graph()
    G_vns = G.copy()
    Failure_vns = Failure.copy()
    Active_vns = Active_normal.copy()
    Backup_vns = Backup_normal.copy()
    [Active_vns,Backup_vns,edge_set] = vns.vns_method(Active_vns,Backup_vns,Failure,j_max,n_hoods,swap_number)
    edge_set_list[0].append(len(edge_set[0]))
    edge_set_list[1].append(len(edge_set[1]))
    initial_cap_normal = rem.total_maximum(Active_normal)
    initial_cap_vns = rem.total_maximum(Active_vns)
    for j in range(len(Active_normal.nodes)-1):
        #[Active_normal,Backup_normal,Active_vns,Backup_vns] = rem.remove_random_node_both(G,Active_normal,Backup_normal,Active_vns,Backup_vns,Failure)
        [Active_normal,Backup_normal] = rem.remove_critical_node(G,Active_normal,Backup_normal,Failure)
        [Active_vns,Backup_vns] = rem.remove_critical_node(G,Active_vns,Backup_vns,Failure)
        [Active_vns,Backup_vns] = rem.graph_flow(G,Active_vns,Backup_vns)
        [Active_normal,Backup_normal] = rem.graph_flow(G,Active_normal,Backup_normal)
        ov_normal = round(100*rem.total_overload(Active_normal)/initial_cap_normal,2)
        ov_vns = round(100*rem.total_overload(Active_vns)/initial_cap_vns,2)
        #print("normal: {} vns: {}".format(ov_normal,ov_vns))
        cap_list_normal[i].append(ov_normal)
        cap_list_vns[i].append(ov_vns)
        cap_list_diff[i].append(ov_normal-ov_vns)

average_normal = [0]*len(cap_list_normal[0])
average_vns = [0]*len(cap_list_normal[0])
average_diff = [0]*len(cap_list_normal[0])
average_edge_set = [st.mean(edge_set_list[0]),st.mean(edge_set_list[1])]

for i in range(iter_metodo):
    for j in range(len(cap_list_normal[0])):
        average_normal[j]+=cap_list_normal[i][j]
        average_vns[j]+=cap_list_vns[i][j]
        average_diff[j]+=cap_list_diff[i][j]

for j in range(len(cap_list_normal[0])):
    average_normal[j]=round(average_normal[j]/iter_metodo,2)
    average_vns[j]=round(average_vns[j]/iter_metodo,2)
    average_diff[j]=round(average_diff[j]/iter_metodo,2)

f= open("dados_remove_random_node.txt","a")
f.write('\n')
f.write('data_normal = {}'.format(average_normal))
f.write('\n')
f.write('data_vns = {}'.format(average_vns))
f.write('\n')
f.write('data_diff = {}'.format(average_diff))
f.write('\n')
f.write('edge_set = {}'.format(average_edge_set))
f.close()

plt.plot(range(len(average_normal)),average_normal,'o-',label = "Normal")
plt.plot(range(len(average_normal)),average_vns,'o-',label = "VNS")
plt.xlabel("Porcentagem de nos removidos",fontsize = 15)
plt.ylabel("Sobrecarga total do grafo",fontsize = 15)
plt.legend(loc=3, prop={'size': 13})
plt.title("Progressao da sobrecarga - Pequeno Mundo",fontsize = 15)
plt.show()
