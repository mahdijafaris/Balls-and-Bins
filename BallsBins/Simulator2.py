# This file is the core implementation of power of two choices.
# Two version of this scheme are implemented. The first one is
# a normal version but the second one is a low memory version
# which is slower but needs less memory. For large networks
# the 'low memory' version should be used.
from __future__ import division
import math
import sys
#import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
#import string
#from BallsBins import *
from BallsBins.Server import Server
from BallsBins.Graph import Gen2DLattice

#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt

def Simulator2(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system

    srv_num, cache_sz, file_num, graph_type = params

    if graph_type == 'RGG': # if the graph is random geometric graph
        rgg_radius = sqrt(5/4*log(srv_num))/sqrt(srv_num)
        # Generate a random geometric graph.
        #print('------------------------------')
        print('Start generating a random geometric graph with {} nodes...'.format(srv_num))
        conctd = False
        while not conctd:
            G = nx.random_geometric_graph(srv_num, rgg_radius)
            conctd = nx.is_connected(G)

        print('Succesfully generates a connected random geometric graph with {} nodes...'.format(srv_num))
    elif graph_type == 'Lattice':
        print('Start generating a square lattice graph with {} nodes...'.format(srv_num))
        G = Gen2DLattice(srv_num)
        print('Succesfully generates a square lattice graph with {} nodes...'.format(srv_num))
    else:
        print("Error: the graph type is not known!")
        sys.exit()
    # Draw the graph
    #nx.draw(G)
    #plt.show()

    # Find all the shortest paths in G
    all_sh_path_len_G = nx.shortest_path_length(G)

#    all_sh_path_G = nx.shortest_path(G)
#    all_sh_path_len_G = {}
#    for src_nd in all_sh_path_G:
#        in_dict = {}
#        for dst_nd in all_sh_path_G[src_nd]:
#            in_dict.update({dst_nd : len(all_sh_path_G[src_nd][dst_nd])-1})
#        all_sh_path_len_G[src_nd] = in_dict
#    print(all_sh_path_G)
#    print(all_sh_path_len_G)
    #quit()

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # List of sets of servers containing each file
    file_sets = [[] for i in range(file_num)]

    # Randomly places cache_sz files in each servers
    print('Randomly places {} files in each server'.format(cache_sz))
    # First put randomly one copy of each file in a subset of servers (assuming file_num =< srv_num)
    lst = np.random.permutation(srv_num)[0:file_num]
    for i, s in enumerate(lst):
        file_sets[i].append(s)
        srvs[s].set_files_list([i])
    # Then fills the rest of empty cache places
    for s in range(srv_num):
        #print(s)
        srvlst = srvs[s].get_files_list()
        list = np.random.permutation(file_num)[0:cache_sz - len(srvlst)]
        srvs[s].set_files_list(srvlst.extend(list))
        for j in range(len(list)):
            if s not in file_sets[list[j]]:
                file_sets[list[j]].append(s)


#    chk = False
#    placement_tries = 0
#    while chk == False:
#        placement_tries += 1
#        print('File placement: try {}'.format(placement_tries))
#        file_sets = [[] for i in range(file_num)] # list of sets of servers containing each file
#        for i in range(srv_num):
#            #print(i)
#            list = np.random.permutation(file_num)[0:cache_sz]
#            srvs[i].set_files_list(list)
#            for j in range(len(list)):
#                if i not in file_sets[list[j]]:
#                    file_sets[list[j]].append(i)
#        chk = True
#        for l in file_sets:
#            if len(l) == 0:
#                chk = False
#                break

    print('Done with randomly placing {} files in each server'.format(cache_sz))

#    print(file_sets)

    # Main loop of the simulator. We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    print('The simulator 2 is starting...')
    total_cost = 0 # Measured in number of hops.
    for i in range(srv_num):
        #print(i)
        incoming_srv = np.random.randint(srv_num) # Random incoming server
        rqstd_file = np.random.randint(file_num) # Random requested file
        if incoming_srv in file_sets[rqstd_file]:
            srv0 = incoming_srv
        else:
            # Find the nearest server that has the requested file
            dmin = 2*srv_num # some large number!
            for nd in file_sets[rqstd_file]:
                #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                d = all_sh_path_len_G[incoming_srv][nd]
                if d < dmin:
                    dmin = d
                    srv0 = nd
#            srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]

        srv1 = srv0
        if len(file_sets[rqstd_file]) > 1:
            while srv1 == srv0:
                srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

        # Implement power of two choices
        load0 = srvs[srv0].get_load()
        load1 = srvs[srv1].get_load()
        if load0 > load1:
            srvs[srv1].add_load()
            #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
            total_cost += all_sh_path_len_G[incoming_srv][srv1]
        elif load0 < load1:
            srvs[srv0].add_load()
            if srv0 != incoming_srv:
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                total_cost += all_sh_path_len_G[incoming_srv][srv0]
        elif np.random.randint(2) == 0:
            srvs[srv0].add_load()
            if srv0 != incoming_srv:
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                total_cost += all_sh_path_len_G[incoming_srv][srv0]
        else:
            srvs[srv1].add_load()
            #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
            total_cost += all_sh_path_len_G[incoming_srv][srv1]

    print('The simulator 2 is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num

#    print(loads)
#    print(maxload)
#    print(total_cost)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost}





def Simulator2_lowmem(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system

    srv_num, cache_sz, file_num, graph_type = params

    if graph_type == 'RGG': # if the graph is random geometric graph
        rgg_radius = sqrt(5/4*log(srv_num))/sqrt(srv_num)
        # Generate a random geometric graph.
        #print('------------------------------')
        print('Start generating a random geometric graph with {} nodes...'.format(srv_num))
        conctd = False
        while not conctd:
            G = nx.random_geometric_graph(srv_num, rgg_radius)
            conctd = nx.is_connected(G)

        print('Succesfully generates a connected random geometric graph with {} nodes...'.format(srv_num))
    elif graph_type == 'Lattice':
        print('Start generating a square lattice graph with {} nodes...'.format(srv_num))
        G = Gen2DLattice(srv_num)
        print('Succesfully generates a square lattice graph with {} nodes...'.format(srv_num))
    else:
        print("Error: the graph type is not known!")
        sys.exit()
    # Draw the graph
    #nx.draw(G)
    #plt.show()

    # Find all the shortest paths in G
#    all_sh_path_len_G = nx.shortest_path_length(G)

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # List of sets of servers containing each file
    file_sets = [[] for i in range(file_num)]

    # Randomly places cache_sz files in each servers
    print('Randomly places {} files in each server'.format(cache_sz))
    # First put randomly one copy of each file in a subset of servers (assuming file_num =< srv_num)
    lst = np.random.permutation(srv_num)[0:file_num]
    for i, s in enumerate(lst):
        file_sets[i].append(s)
        srvs[s].set_files_list([i])
    # Then fills the rest of empty cache places
    for s in range(srv_num):
        #print(s)
        srvlst = srvs[s].get_files_list()
        list = np.random.permutation(file_num)[0:cache_sz - len(srvlst)]
        srvs[s].set_files_list(srvlst.extend(list))
        for j in range(len(list)):
            if s not in file_sets[list[j]]:
                file_sets[list[j]].append(s)

    print('Done with randomly placing {} files in each server'.format(cache_sz))

#    print(file_sets)

    # Main loop of the simulator. We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    print('The simulator 2 is starting...')
    total_cost = 0 # Measured in number of hops.
    for i in range(srv_num):
        #print(i)
        incoming_srv = np.random.randint(srv_num) # Random incoming server
        rqstd_file = np.random.randint(file_num) # Random requested file
        all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)
        if incoming_srv in file_sets[rqstd_file]:
            srv0 = incoming_srv
        else:
            # Find the nearest server that has the requested file
            dmin = 2*srv_num # some large number!
            for nd in file_sets[rqstd_file]:
                #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                d = all_sh_path_len_G[nd]
                if d < dmin:
                    dmin = d
                    srv0 = nd
#            srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]

        srv1 = srv0
        if len(file_sets[rqstd_file]) > 1:
            while srv1 == srv0:
                srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

        # Implement power of two choices
        load0 = srvs[srv0].get_load()
        load1 = srvs[srv1].get_load()
        if load0 > load1:
            srvs[srv1].add_load()
            #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
            total_cost += all_sh_path_len_G[srv1]
        elif load0 < load1:
            srvs[srv0].add_load()
            if srv0 != incoming_srv:
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                total_cost += all_sh_path_len_G[srv0]
        elif np.random.randint(2) == 0:
            srvs[srv0].add_load()
            if srv0 != incoming_srv:
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                total_cost += all_sh_path_len_G[srv0]
        else:
            srvs[srv1].add_load()
            #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
            total_cost += all_sh_path_len_G[srv1]

    print('The simulator 2 is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num

#    print(loads)
#    print(maxload)
#    print(total_cost)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost}