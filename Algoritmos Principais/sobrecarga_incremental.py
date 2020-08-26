#!/usr/bin/env python
# coding: utf-8

# In[1]:


import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import operator
import removal_and_reconfiguration_functions as rem
import utils as ut
import VNS as vns
import numpy as np
import statistics as st


# In[2]:


def add_k_best_edges(G,k):
    cap_dict = {}
    k = 2
    for i in G.nodes():
        cap_dict[i] = G.nodes[i]['capacity']

    sorted_cap = sorted(cap_dict.items(), key=operator.itemgetter(1),reverse = True)
    for i in range(k):
        if (sorted_cap[k],sorted_cap[k+1]) not in G.edges():
            G.add_edge(sorted_cap[k][0],sorted_cap[k+1][0],flow = round((alpha)*max(sorted_cap[k][1],sorted_cap[k+1][1]),2))
        else:
            pass


# In[3]:

data_node = pd.read_csv('dados70barras_node.csv')
data_edge = pd.read_csv('dados70barras_edge.csv')

mean_edge = data_edge['potencia'].mean()
std_edge = data_edge['potencia'].std()
mean_node = data_node['potencia_no'].mean()
std_node = data_node['potencia_no'].std()


# In[4]:


'''Grafo_londrina = nx.Graph()

for i in range(len(data_node)):
    Grafo_londrina.add_node(data_node['barra'][i],capacity = data_node['potencia_no'][i])

for i in range(len(data_edge)):
    Grafo_londrina.add_edge(data_edge['de'][i],data_edge['para'][i],flow = data_edge['potencia'][i])
'''


# In[5]:
#nodes_removed_list = [0.3]
graph_size_list = [600] #posteriormente fazer com 600, 3000 e 30000 nós
carregamento_list = [0.9]
overload_list = [0.2]
alpha_list = [2]
r = 1#redundância
j_max = 500 #numero maximo de execucoes do metodo VNS
n_hoods = 0 #numero de vizinhancas a ser utilizado
swap_number = 1 #numero de trocas de arestas a serem feitas


# In[6]:
for i in range(2):
    data_normal = np.zeros((len(graph_size_list),len(carregamento_list),len(overload_list),len(alpha_list)))
    data_vns = np.zeros((len(graph_size_list),len(carregamento_list),len(overload_list),len(alpha_list)))
    data_score = np.zeros((len(graph_size_list),len(carregamento_list),len(overload_list),len(alpha_list)))
    for index_graph in range(len(graph_size_list)):
        for index_carregamento in range(len(carregamento_list)):
            for index_overload in range(len(overload_list)):
                for index_alpha in range(len(alpha_list)):
                    print('{},{},{},{}'.format(index_graph,index_carregamento,index_overload,index_alpha))
                    graph_size = graph_size_list[index_graph]
                    carregamento = carregamento_list[index_carregamento]
                    overload_porc = overload_list[index_overload]
                    alpha = alpha_list[index_alpha]
                    G = rem.create_directed_graph(nx.watts_strogatz_graph(graph_size,int(round(graph_size/100)),0.5))
                    #G = rem.create_directed_graph(nx.scale_free_graph(graph_size))
                    #G = nx.grid_2d_graph(graph_size,graph_size)
                    #G = Grafo_londrina
                    rem.set_nodes_capacity(G,50,5)
                    rem.set_edges_flow(G,alpha)
                    rem.set_nodes_maximum(G,carregamento)
                    Active = rem.set_active_graph(G)
                    print(len(Active.nodes()))
                    Backup = rem.set_backup_graph(G,Active,1)
                    Failure = rem.set_failure_graph()
                    #rem.remove_porcentagem_random_nodes(G,Active,Backup,Failure,nodes_removed)
                    #for i in range(int(round(1.3*(1-carregamento)*len(Active.nodes())))):
                        #rem.add_random_overload(Active,Backup,Failure)
                    maximo = rem.total_maximum(Active)
                    overload = 0
                    while overload <= overload_porc*maximo: #determina qual a porcentagem do maximo que sera convertido em sobrecarga
                        overload += rem.add_random_overload(Active,Backup,Failure)
                    #for i in range(int(round(0.3*len(Active.nodes()),1))): #metodo para a remocao de nós
                    #size = 0
                    #for i in range(5):
                        #rem.remove_highest_degree_node(G,Active,Backup,Failure,size)
                        #size+=1
                    print(rem.total_overload(Active))
                    vns_data = vns.graph_flow_comparison(G,Active,Backup,Failure,j_max,n_hoods,swap_number)
                    data_normal[index_graph][index_carregamento][index_overload][index_alpha] = vns_data[0]
                    data_vns[index_graph][index_carregamento][index_overload][index_alpha] = vns_data[1]
                    data_score[index_graph][index_carregamento][index_overload][index_alpha] = vns_data[2][0]
                    #salvar os dados em um arquivo txt

                    f= open("dados_carregamento.txt","a")
                    f.write('\n')
                    f.write('Vetor tamanho do grafo: {}\nVetor carregamento: {}\nVetor porcentagem de sobrecarga: {}\nAlpha: {}\nr: {}\nj_max: {}\nn_hoods: {}\nswap_number: {}\n'.format(graph_size_list[index_graph],carregamento_list[index_carregamento],overload_list[index_overload],alpha,r,j_max,n_hoods,swap_number))
                    f.write('data_normal:{}'.format(data_normal[index_graph][index_carregamento][index_overload][index_alpha]))
                    f.write('\n')
                    f.write('data_vns:{}'.format(data_vns[index_graph][index_carregamento][index_overload][index_alpha]))
                    f.write('\n')
                    f.write('data_score:{}'.format(data_score[index_graph][index_carregamento][index_overload][index_alpha]))
                    f.write('\n')
                    f.write('-------------------------------------\n')
                    f.close()

    f= open("dados_carregamento.txt","a")
    f.write('\n')
    f.write('data_normal:{}'.format(data_normal))
    f.write('\n')
    f.write('data_vns:{}'.format(data_vns))
    f.write('\n')
    f.write('data_score:{}'.format(data_score))
    f.write('\n')
    f.close()






# In[ ]:


'''data_compara = np.zeros((len(graph_size_list),len(carregamento_list),len(overload_list)))
data_sim = 0
data_nao = 0
for index_graph in range(len(graph_size_list)):
    for index_carregamento in range(len(carregamento_list)):
        for index_overload in range(len(overload_list)):
            data_compara[index_graph][index_carregamento][index_overload] = (data_vns[index_graph][index_carregamento][index_overload] - data_normal[index_graph][index_carregamento][index_overload])
            if(data_compara[index_graph][index_carregamento][index_overload] >= 0):
                data_sim+=1
            else:
                data_nao+=1

data_bit = float(data_sim)/(data_sim+data_nao)'''
