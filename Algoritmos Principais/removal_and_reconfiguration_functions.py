import networkx as nx
import random
import utils as ut
import statistics as st
import numpy as np
import collections
import operator


###################################
# GRAPH SETUP
##################################


def set_nodes_maximum(G,carregamento):
    for i in G.nodes():
        try:
            G.nodes[i]['max'] = G.nodes[i]['capacity']/carregamento
            '''round(random.randint(50,150)*G.nodes[i]['capacity']/100,2)'''
        except KeyError:
            G.nodes[i]['max'] = 0

def set_nodes_capacity(G,mean,variance):
    for i in G.nodes():
        try:
            '''G.nodes[i]['capacity'] = G.nodes[i]['capacity']'''
            G.nodes[i]['capacity'] = abs(round(G.degree(i)*np.random.normal(mean,variance),0))
        except KeyError:
            print("keyerror")
            G.nodes[i]['capacity'] = 0

def set_edges_flow(G,alpha):
    for i,j in G.edges():
        try:
            numero = round((alpha)*max(G.nodes[i]['capacity'],G.nodes[j]['capacity']),2)
            G[i][j]['flow'] = np.random.normal(numero,numero/2)
            '''G[i][j]['flow'] = 1000'''
        except KeyError:
            print('keyerror')
            G[i][j]['flow'] = 0

def set_active_graph(G):
    Active_graph = G.copy()
    num_edges = len(G.edges)
    edges = ut.unpack_list(Active_graph.edges())
    for i in range(int(round(num_edges/4))):
        chosen_edge = random.choice(edges)
        Active_graph.remove_edge(*chosen_edge)
        edges.remove(chosen_edge)
    return Active_graph

def set_backup_graph(G,Active_graph,r):
    Prov = G.copy()
    Prov.remove_edges_from(Active_graph.edges())
    edges = ut.unpack_list(Prov.edges())
    for i in range(int(round((1-r)*(len(edges))))):
        rand = random.choice(edges)
        Prov.remove_edge(*rand)
        edges.remove(rand)
    return Prov

def set_failure_graph():
    G_failure = nx.Graph()
    return G_failure

def set_total_graph(Backup,Active):
    x = nx.compose(Backup,Active)
    return x

def activate_backup_graph(Active_graph,Backup_graph,path):
    for i in range(len(path)-1):
        y = (path[i],path[i+1])
        if y in Backup_graph.edges():
            Active_graph.add_edge(*y,flow = Backup_graph[y[0]][y[1]]['flow'])
            Backup_graph.remove_edge(*y)

def add_k_best_edges(G,k): #lembrar que, na maioria dos casos, queremos adicionar no Backup (colocar Backup no argumento da funcao)
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


###########################################
    #REMOVAL FUNCTIONS
###########################################
def remove_random_edge(Active,Backup,Failure):
    Total = set_total_graph(Active, Backup)
    x = random.choice(ut.unpack_list(Total.edges()))
    if x in Backup.edges():
        Failure.add_edge(*x,flow = Backup[x[0]][x[1]]['flow'])
        Backup.remove_edge(*x)
    if x in Active.edges():
        Failure.add_edge(*x,flow = Active[x[0]][x[1]]['flow'])
        Active.remove_edge(*x)
    Total.remove_edge(*x)
    Failure.nodes[x[0]]['capacity'] = 0
    Failure.nodes[x[1]]['capacity'] = 0

def remove_highest_flow_edge(Active,Backup,Failure):
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

def remove_random_node(G,Active,Backup,Failure):
    Total = set_total_graph(Active,Backup)
    x = random.choice(ut.unpack_list(Total.nodes()))
    if x in Active.nodes():
        Failure.add_node(x,capacity = Active.nodes[x]['capacity'])
        short_overload_flow(x,Active,Backup)
        #last_case_flow(Active,Backup,x,1)
        #adj_energy_flow(Active,Backup,x,1)
        Active.remove_node(x)
        Backup.remove_node(x)
    return [Active,Backup]

def remove_random_node_both(G,Active_normal,Backup_normal,Active_vns,Backup_vns,Failure):
    Total = set_total_graph(Active_normal,Backup_normal)
    x = random.choice(ut.unpack_list(Total.nodes()))
    if x in Active_normal.nodes():
        Failure.add_node(x,capacity = Active_normal.nodes[x]['capacity'])
        #short_overload_flow(x,Active_normal,Backup_normal)
        #short_overload_flow(x,Active_vns,Backup_vns)
        #last_case_flow(Active_normal,Backup_normal,x)
        #last_case_flow(Active_vns,Backup_vns,x)
        adj_energy_flow(Active_normal,Backup_normal,x,1)
        adj_energy_flow(Active_vns,Backup_vns,x,1)
        Active_normal.remove_node(x)
        Backup_normal.remove_node(x)
        Active_vns.remove_node(x)
        Backup_vns.remove_node(x)
    return [Active_normal,Backup_normal,Active_vns,Backup_vns]

def remove_critical_node(G,Active,Backup,Failure):
    dict = nx.betweenness_centrality(Active)
    x = max(dict.iteritems(), key=operator.itemgetter(1))[0]
    if x in Active.nodes():
        Failure.add_node(x,capacity = Active.nodes[x]['capacity'])
        #short_overload_flow(x,Active,Backup)
        last_case_flow(Active,Backup,x)
        #adj_energy_flow(Active,Backup,x,1)
        Active.remove_node(x)
        Backup.remove_node(x)
    return [Active,Backup]

def remove_critical_node_both(G,Active_normal,Backup_normal,Active_vns,Backup_vns,Failure):
    Total = set_total_graph(Active_normal,Backup_normal)
    dict = nx.betweenness_centrality(Active_normal)
    x = max(dict.iteritems(), key=operator.itemgetter(1))[0]
    if x in Active_normal.nodes():
        Failure.add_node(x,capacity = Active_normal.nodes[x]['capacity'])
        short_overload_flow(x,Active_normal,Backup_normal)
        short_overload_flow(x,Active_vns,Backup_vns)
        #last_case_flow(Active_normal,Backup_normal,x)
        #last_case_flow(Active_vns,Backup_vns,x)
        Active_normal.remove_node(x)
        Backup_normal.remove_node(x)
        Active_vns.remove_node(x)
        Backup_vns.remove_node(x)
    return [Active_normal,Backup_normal,Active_vns,Backup_vns]

def remove_k_random_edges(Active,Backup,Failure,k):
    for i in range(k):
        remove_random_edge(Active,Backup,Failure)

def remove_k_random_nodes(G,Active,Backup,Failure,k):
    for i in range(k):
        remove_highest_degree_node(G,Active,Backup,Failure)
        '''print(ut.pandas_print(Active))'''

def remove_porcentagem_random_nodes(G,Active,Backup,Failure,porc):
    k = int(round(porc*len(G.nodes),0))
    for i in range(k):
        remove_random_node(G,Active,Backup,Failure)

def set_edges_to_0(Active,Node):
    for i in Active.adj[Node]:
        Active[Node][i]['flow'] = 0



###################################################
#          EDGE RECONFIGURATION                   #
###################################################

def create_edges_energy_capacity(G):
    for i in G.edges:
        G[i[0]][i[1]]['flow']=random.randint(0,20)

def find_paths(G,giver,taker):
    paths = list(nx.all_simple_paths(G,giver,taker))
    paths.sort(key=len)
    return paths

def check_valid_flow(G,giver,taker,flow):
    paths = find_paths(G,giver,taker)
    deu_certo = False
    for i in paths:
        check = True
        for j in range((len(i)-1)):
            if G[i[j]][i[j+1]]['flow'] < flow:
                check = False
        if check:
            deu_certo = True
            break
    return deu_certo

def find_right_flow_path(G,giver,taker,set_flow):
    paths = find_paths(G,giver,taker)
    paths_x_maxflow = {}
    check = True
    k = -1
    for i in paths: #verifica todos os paths, um por um, ate achar algum que satisfaca
        k+=1
        flow = []
        for j in range((len(i)-1)):
            flow.append(G[i[j]][i[j+1]]['flow'])
        paths_x_maxflow[k] = min(flow)
        '''if paths_x_maxflow[k] >= set_flow:
            best_flow = paths_x_maxflow[k]
            path = paths[ut.find_key_by_value(paths_x_maxflow,best_flow)]
            check = False
            break'''
    '''if check:
        best_flow = 0
        path = []'''
    best_flow = max(paths_x_maxflow.values())
    path = paths[ut.find_key_by_value(paths_x_maxflow,best_flow)]
    return [best_flow, path] #primeiro -> valor do flow maximo segundo -> path que gera esse flow

def find_and_activate_alt_path(Active,Backup,Failure): #para os edges que sofreram falha, verifica se ha outro caminho alternativo para ligar os mesmos nos
    Total = set_total_graph(Active,Backup)
    for i,j in Failure.edges:
        if nx.has_path(Total,i,j):
            alt_path = find_right_flow_path(Total,i,j)[1]
            activate_backup_graph(Active,Backup,alt_path)



###############################################
# NODE RECONFIGURATION
###############################################

def create_nodes_energy_capacity(G):
    for i in G.nodes:
        G.nodes[i]['capacity']=0
        for j in G.adj[i]:
            G.nodes[i]['capacity']+=G[i][j]['flow']

def adj_escolhido(G,node):
    dict = {}
    for i in G.adj[node]:
        k = 0
        for j in G.adj[i]:
            flow = G.nodes[j]['max'] - G.nodes[j]['capacity']
            if flow > 0:
                k+=flow
        dict[i] = k
    maximum_extra = max(dict.values())
    for i,j in dict.items():
        if j == maximum_extra:
            taker = i
    return taker

############################################
# EDGE FLOW METHODS
############################################
def long_energy_flow(G,giver,Backup,Active):
    global total_path_len
    Total = set_total_graph(Backup,Active)
    g = Active.nodes[giver]['capacity']
    parcial_path_len = []
    if g > Active.nodes[giver]['max']:
        for i in Total.nodes():
            t = Total.nodes[i]['capacity']
            if t < Total.nodes[i]['max'] and nx.has_path(Total,giver,i):
                flow = Total.nodes[i]['max'] - t
                '''print("Giver:{} Taker: {}".format(giver,i))
                print(list(nx.all_shortest_paths(G,giver,i)))'''
                taker_flow = find_right_flow_path(Active,giver,i,flow) #IMPORTANTE: Aqui eu mudei de Total para Active, para que o metodo em long em si nao faca novas conexoes
                if (taker_flow[0] >= flow):
                    long_takers = flow
                else:
                    long_takers = taker_flow[0] #taker_flow[0] eh o valor da transferencia
                path = taker_flow[1] #taker_flow[1] representa o path que sera utilizado para transferencia, e que deve ser ativado
                '''activate_backup_graph(Active,Backup,path)'''
                Backup.nodes[i]['capacity'] += long_takers
                Backup.nodes[giver]['capacity'] -= long_takers
                Active.nodes[i]['capacity'] += long_takers
                Active.nodes[giver]['capacity']-= long_takers
                parcial_path_len.append(len(path))

    return len(parcial_path_len)

def adj_energy_flow(Active,Backup,giver,removal_flag):
    Total = Active.copy()
    if removal_flag:
        g = Total.nodes[giver]['capacity']
    else:
        g = Total.nodes[giver]['capacity'] - Total.nodes[giver]['max']
    if (g > 0):
        flow_giver = g
        flow_list = {}
        for i in Total.adj[giver]:
            taker_cap = Total.nodes[i]['max'] - Total.nodes[i]['capacity']
            taker_flow = Total[giver][i]['flow']
            if taker_cap > 0:
                if taker_cap > taker_flow:
                    flow_list[(giver,i)] = taker_flow
                else:
                    flow_list[(giver,i)] = taker_cap
            else:
                flow_list[(giver,i)] = 0
        total_flow=sum(flow_list.values())
        if total_flow >= flow_giver: #checa se apenas os nos adjacentes sao capazes de acabar com a sobrecarga
            #sorted_dict = flow_list
            for i in flow_list:
                flow_list[i] = (flow_list[i]*flow_giver)/total_flow
            sorted_flow = sorted(flow_list.items(), key=lambda kv: kv[1],reverse=True)
            sorted_dict = collections.OrderedDict(sorted_flow)
            for i,j in sorted_dict.items():
                if removal_flag:
                    flow_giver = Active.nodes[giver]['capacity']
                else:
                    flow_giver = Active.nodes[giver]['capacity'] - Active.nodes[giver]['max']
                if flow_giver > 0:
                    path = [giver,i[len(i)-1]]
                    activate_backup_graph(Active,Backup,path)
                    #if flow_giver < sorted_dict[i]:
                        #sorted_dict[i] = flow_giver
                    Backup.nodes[i[len(i)-1]]['capacity'] += sorted_dict[i]
                    Backup.nodes[giver]['capacity'] -= sorted_dict[i]
                    Active.nodes[i[len(i)-1]]['capacity'] += sorted_dict[i]
                    Active.nodes[giver]['capacity']-= sorted_dict[i]
                else:
                    break
        else: #aqui comeca a fazer para o segundo "grau" de adjacencia
            repeat = [] #evita que um mesmo no seja contabilizado duas vezes
            for i in Total.adj[giver]:
                for j in Total.adj[i]:
                    if j!=giver and (j not in repeat):
                        repeat.append(j)
                        #print(j)
                        taker_cap = Total.nodes[j]['max'] - Total.nodes[j]['capacity']
                        taker_flow = min(Total[giver][i]['flow'],Total[i][j]['flow'])
                        if taker_cap > 0:
                            if taker_cap > taker_flow:
                                flow_list[i,j] = taker_flow
                            else:
                                flow_list[i,j] = taker_cap
                        else:
                            flow_list[i,j] = 0
            total_flow=sum(flow_list.values())
            if total_flow >= flow_giver:
                for i in flow_list:
                    flow_list[i] = (flow_list[i]*flow_giver)/total_flow
                sorted_flow = sorted(flow_list.items(), key=lambda kv: kv[1],reverse=True)
                sorted_dict = collections.OrderedDict(sorted_flow)
                for i,j in sorted_dict.items():
                    path = [giver,i[len(i)-1]]
                    activate_backup_graph(Active,Backup,path)
                    if removal_flag:
                        flow_giver = Total.nodes[giver]['capacity']
                    else:
                        flow_giver = Total.nodes[giver]['capacity'] - Total.nodes[giver]['max']
                    if flow_giver > 0:
                        Backup.nodes[i[len(i)-1]]['capacity'] += sorted_dict[i]
                        Backup.nodes[giver]['capacity'] -= sorted_dict[i]
                        Active.nodes[i[len(i)-1]]['capacity'] += sorted_dict[i]
                        Active.nodes[giver]['capacity']-= sorted_dict[i]
                    else:
                        break
            else:
                if(removal_flag):
                    last_case_flow(Active,Backup,giver)
    return [Active,Backup]

def short_overload_flow(giver,Active,Backup):
    transf = {}
    flow = {}
    giver_flow = Active.nodes[giver]['capacity']
    for i in Active.adj[giver]:
        teste = Active.nodes[i]['max'] - Active.nodes[i]['capacity']
        if teste > 0:
            flow[i] = teste
        else:
            flow[i] =  0
    total_flow = sum(flow.values())
    for i in Active.adj[giver]:
        try:
            transf[i] = round((flow[i]*giver_flow)/total_flow,2)
        except ZeroDivisionError:
            transf[i] = 0
        if Active[i][giver]['flow'] < transf[i]:
            transf[i] = Active[giver][i]['flow']
        Active.nodes[i]['capacity'] += transf[i]
        Active.nodes[giver]['capacity']-= transf[i]
        Backup.nodes[i]['capacity'] += transf[i]
        Backup.nodes[giver]['capacity']-= transf[i]


def last_case_flow(Active,Backup,giver): #evita a sobrecarga do no em questao, mas os nos adjacentes podem passar a ter sobrecarga
    flow = {}
    for i in Active.adj[giver]:
        try:
            flow[i] = round((Active.nodes[giver]['capacity'])/Active.degree[giver],2)
        except ZeroDivisionError:
            flow = 0
        if Active[i][giver]['flow'] < flow[i]:
            flow[i] = Active[giver][i]['flow']
        Active.nodes[i]['capacity'] += flow[i]
        Backup.nodes[i]['capacity'] += flow[i]
        Active.nodes[giver]['capacity'] -= flow[i]
        Backup.nodes[giver]['capacity'] -= flow[i]


'''def graph_flow(G,Backup,Active):
    total_path_len = []
    active_before = len(Active.edges())
    for i in Active.nodes():
        parcial = long_energy_flow(G,i,Backup,Active)
        if (parcial != None):
            total_path_len.append(parcial)
    active_after = len(Active.edges())

    try:
        reconf_rate = round(100*(active_after - active_before)/active_before,2)
    except ZeroDivisionError:
        reconf_rate = 0
    mean_path_size = round(st.mean(total_path_len),2)
    return [reconf_rate,mean_path_size]'''
def graph_flow(G,Active,Backup):
    for i in Active.nodes():
        [Active,Backup] = adj_energy_flow(Active,Backup,i,0)
    return [Active,Backup]


##################################
# FAILURE DETECTION
##################################

def node_overload_detection(G):
    overload_nodes = [i for i in G.nodes() if G.nodes[i]['capacity'] > G.nodes[i]['max']]
    return overload_nodes

##################################
# MEASURE FUNCTIONS
##################################

def measure_overload_rate(G): #porcentagem dos nos no grafo que estao com sobrecarga
    overload_list = [i for i in G.nodes if G.nodes[i]['capacity'] > G.nodes[i]['max']]
    rate = len(overload_list)/len(G.nodes)
    return 100*rate

def total_capacity(G):
    total_cap = [G.nodes[i]['capacity'] for i in G.nodes()]
    return round(sum(total_cap),2)

def total_overload(G): #quantidade total de capacidade que esta sobrecarregada
    flow_list = [(G.nodes[i]['capacity'] - G.nodes[i]['max']) for i in G.nodes if G.nodes[i]['capacity'] > G.nodes[i]['max']]
    return round(sum(flow_list),2)

def total_maximum(G):
    maximum_list = [G.nodes[i]['max'] for i in G.nodes()]
    return round(sum(maximum_list),2)

def variance_node_capacity(G):
    capacity_list = [G.nodes[i]['capacity'] for i in G.nodes]
    return round(st.variance(capacity_list),2)

def average_edge_flow(G):
    total_flow = [G[i[0]][i[1]]['flow'] for i in G.edges()]
    return round(st.mean(total_flow),2)

def weighted_edge_flow(G):
    total_weighted_flow = [(G[i[0]][i[1]]['flow'])*(G.degree[i[0]]+G.degree[i[1]]) for i in G.edges()]
    return round(st.mean(total_weighted_flow),2)

def average_degree(G):
    ave_degree = [G.degree[i] for i in G.nodes]
    return round(st.mean(ave_degree),2)

def carregamento(G):
    maximum = total_maximum(G)
    load = total_capacity(G)
    return round(load/maximum,2)

def graph_redistribution_check(G): #checa se o overload poderia ser redistribuido ao longo de todo o grafo (desconsiderando falhas nas arestas)
    check = False
    maximum = total_maximum(G)
    capacity = total_capacity(G)
    if (maximum > capacity):
        check = True
    return check

def check_capacity_decrease(Removed_graph,Initial_graph):
    Initial_cap = total_capacity(Initial_graph)
    Removed_cap = total_capacity(Removed_graph)
    rem25,rem50,rem75 = 0,0,0
    if Removed_cap <= 0.25*Initial_cap:
        rem25 = round(100*(len(Initial_graph.nodes()) - len(Removed_graph.nodes()))/len(Initial_graph.nodes()),2)
    elif Removed_cap <= 0.50*Initial_cap:
        rem50 = round(100*(len(Initial_graph.nodes()) - len(Removed_graph.nodes()))/len(Initial_graph.nodes()),2)
    elif Removed_cap <= 0.75*Initial_cap:
        rem75 = round(100*(len(Initial_graph.nodes()) - len(Removed_graph.nodes()))/len(Initial_graph.nodes()),2)

    return [rem25,rem50,rem75]

def create_directed_graph(G):
    H = nx.Graph()
    H.add_nodes_from(list(G.nodes()))
    H.add_edges_from(list(G.edges()))
    return H


###################################
# RECONSTRUCTION FUNCTIONS
###################################

def activate_random_edge(Active,Backup,Failure):
    x = random.choice(ut.unpack_list(Backup.edges()))
    Active.add_edge(*x,flow = Backup[x[0]][x[1]]['flow'])
    Backup.remove_edge(*x)
    return x

def add_random_overload(Active,Backup,Failure):
    x = random.choice(ut.unpack_list(Active.nodes()))
    inc = round(Active.nodes[x]['capacity']/20,2)
    Active.nodes[x]['capacity']+=inc
    Backup.nodes[x]['capacity']+=inc
    return inc

def add_intentional_overload(Active,Backup,Failure,k):
    list = ut.unpack_list(sorted(Active.nodes(), key = Active.degree,reverse = 1))
    node = list[0]
    inc = k*Active.nodes[node]['max']
    Active.nodes[node]['capacity']+=inc
    Backup.nodes[node]['capacity']+=inc
    return node
