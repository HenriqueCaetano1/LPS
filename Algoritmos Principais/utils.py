import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections
import networkx as nx

def teste():
    print("banana")

def unpack_list(list):
    unpacked_list = []
    for i in list:
        unpacked_list.append(i)
    return unpacked_list

def find_key_by_value(dictionary,value):
    for i,j in dictionary.items():
        if j == value:
            return i

def print_maximum(G):
    for i in G.nodes():
        print("{}: {}".format(i, G.nodes[i]['max']))

def print_capacity(G):
    for i in G.nodes():
        print("{}: {}".format(i, G.nodes[i]['capacity']))

def pretty_print(G,Active,Backup,Failure): #OBS: transformar em uma tabela usando o pandas, posteriormente
    print("Active")
    for i in Active.nodes():
        print("{}: {}".format(i, Active.nodes[i]['capacity']))
    print("Backup")
    for i in Backup.nodes():
        print("{}: {}".format(i, Backup.nodes[i]['capacity']))
    print("Failure")
    for i in Failure.nodes():
        print("{}: {}".format(i, Failure.nodes[i]['capacity']))


def pandas_print(G):
    Nodes = []
    Capacities = []
    Maximum = []
    Degree = []
    for i in G.nodes:
        Nodes.append(i)
        Capacities.append(G.nodes[i]['capacity'])
        Maximum.append(G.nodes[i]['max'])
        Degree.append(G.degree(i))
    Nodes.append("--")
    Capacities.append(sum(Capacities))
    Maximum.append(sum(Maximum))
    Degree.append(sum(Degree)/len(Degree))

    info = pd.DataFrame({'Nodes': Nodes,'Capacity': Capacities,'Maximum': Maximum, "Degree":Degree,})
    return info

def edges_print(G):
    Edge = []
    Flow = []
    for i in G.edges():
        edges = unpack_list(i)
        Edge.append(i)
        Flow.append(G[edges[0]][edges[1]]['flow'])
    info = pd.DataFrame({'Edges':Edge,'Flow':Flow})
    return info

def degree_histogram(G):
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.show()

def difference(Antigo, Novo):
    DIF = nx.create_empty_copy(Antigo)
    if set(Antigo) != set(Novo):
        raise nx.NetworkXError("Node sets of graphs is not equal")

    a_edges = set(Antigo.edges())
    n_edges = set(Novo.edges())


    # In case it is the difference:
    #diff_edges = r_edges.symmetric_difference(s_edges)

    adicionar = n_edges - a_edges
    remover = a_edges - n_edges
    return adicionar,remover
