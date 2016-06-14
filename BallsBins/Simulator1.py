# This file simulates the randomly selection of the server
# but there is no power of two choices.
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

def Simulator1(params):
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

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # List of sets of servers containing each file
    # the outer list is indexed by the files
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

    # Main loop of the simulator. We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    print('The simulator 1 is starting...')
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
            total_cost = total_cost + dmin
#            srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]
#            total_cost = total_cost + nx.shortest_path_length(G, source=incoming_srv, target=srv0)

        # Implement random placement without considering loads
        srvs[srv0].add_load()


#    srv1 = srv0
#    if len(file_sets[rqstd_file]) > 1:
#        while srv1 == srv0:
#            srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]
#

    print('The simulator 1 is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num

#    print(loads)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost}



def Simulator1_lowmem(params):
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
    # the outer list is indexed by the files
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

    # Main loop of the simulator. We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    print('The simulator 1 is starting...')
    total_cost = 0 # Measured in number of hops.
    for i in range(srv_num):
        #print(i)
        incoming_srv = np.random.randint(srv_num) # Random incoming server
        rqstd_file = np.random.randint(file_num) # Random requested file
        if incoming_srv in file_sets[rqstd_file]:
            srv0 = incoming_srv
        else:
            # Find the nearest server that has the requested file
            all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)
            dmin = 2*srv_num # some large number!
            for nd in file_sets[rqstd_file]:
                #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                d = all_sh_path_len_G[nd]
                if d < dmin:
                    dmin = d
                    srv0 = nd
            total_cost = total_cost + dmin
#            srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]
#            total_cost = total_cost + nx.shortest_path_length(G, source=incoming_srv, target=srv0)

        # Implement random placement without considering loads
        srvs[srv0].add_load()


#    srv1 = srv0
#    if len(file_sets[rqstd_file]) > 1:
#        while srv1 == srv0:
#            srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]
#

    print('The simulator 1 is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num

#    print(loads)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost}
