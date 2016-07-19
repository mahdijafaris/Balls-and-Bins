# This files simulate the trade-off between minimum communication cost scheme and
# minimum load scheme.
#
# Here we implement the power of two choices. However we change radius of search
# for finding two bins. By changing this radius, we will have different trade-offs.

from __future__ import division
import math
import sys
import networkx as nx
import numpy as np
from BallsBins.Server import Server
from BallsBins.Graph import Gen2DLattice

#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt

def Simulator3(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system
    # alpha: alpha determines the search space as follows: (1+alpha)NearestNeighborDistance

    srv_num, cache_sz, file_num, graph_type, alpha = params

    # Check the validity of parameters
    if cache_sz > file_num:
        print("Error: The cache size is larger that number of files!")
        sys.exit()

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

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # List of sets of servers containing each file. The list is enumerate by the
    # file index and for each file we have a list that contains the servers cached that file.
    file_sets = [[] for i in range(file_num)]

    # Randomly places cache_sz files in each servers
    print('Randomly places {} files in each server'.format(cache_sz))
    # First put randomly one copy of each file in a subset of servers (assuming file_num =< srv_num)
    lst = np.random.permutation(srv_num)[0:file_num]
    for i, s in enumerate(lst):
        file_sets[i].append(int(s))
        srvs[s].set_files_list([i])
    # Then fills the rest of empty cache places
    for s in range(srv_num):
        #print(type(s))
        srvlst = srvs[s].get_files_list()
        rnd_lst = np.random.permutation(file_num)[0:cache_sz - len(srvlst)]
        #rnd_lst = [int(l) for l in rnd_lst]
        srvs[s].set_files_list(srvlst.extend(rnd_lst))
        for j in range(len(rnd_lst)):
            if s not in file_sets[rnd_lst[j]]:
                file_sets[rnd_lst[j]].append(s)

    print('Done with randomly placing {} files in each server'.format(cache_sz))


    # Main loop of the simulator. We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    # Then we apply the power of two choices scheme but up to some radius from the requsting
    # node.
    print('The simulator 3 is starting...\
          with parameters: sn={}, cs={}, fn={}, graph_type={}, alpha={}'\
          .format(srv_num, cache_sz, file_num, graph_type, alpha))
    total_cost = 0 # Measured in number of hops.
    for i in range(srv_num):
        #print(i)
        incoming_srv = np.random.randint(srv_num) # Random incoming server
        rqstd_file = np.random.randint(file_num) # Random requested file

        # Find the shortest path from requesting nodes to all other nodes
        all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)

        # Find the nearest server that has the requested file
#        print(file_sets[rqstd_file])
#        print(type(file_sets[rqstd_file][0]))
#        print(list(file_sets[rqstd_file]))
        nearest_neighbor = []
        srv_lst_for_this_request_excld_incom_srv = list(file_sets[rqstd_file])
        if incoming_srv in file_sets[rqstd_file]:
            srv_lst_for_this_request_excld_incom_srv.remove(incoming_srv)
#        print(srv_lst_for_this_request_excld_incom_srv)
        if len(srv_lst_for_this_request_excld_incom_srv) > 0:
            dmin = 2*srv_num # some large number, eg, larger that the graph diameter!
            for nd in srv_lst_for_this_request_excld_incom_srv:
                #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                dtmp = all_sh_path_len_G[nd]
                if dtmp < dmin:
                    dmin = dtmp
                    nearest_neighbor = nd
#        print(file_sets[rqstd_file])
#        print(srv_lst_for_this_request_excld_incom_srv)

        if incoming_srv in file_sets[rqstd_file]:
            srv0 = incoming_srv
        else:
            srv0 = nearest_neighbor

        # Up to this point, we set srv1 also to be the same as srv0
        srv1 = srv0

        twochoice_search_space = []
        if len(file_sets[rqstd_file]) > 1:
            # Now we have to find a subset of nodes that have the requested file and
            # are within a distant "(1+alpha)*dmin" from the requesting server.
            for nd in file_sets[rqstd_file]:
                if all_sh_path_len_G[nd] <= (1+alpha)*dmin and nd != srv0:
                    twochoice_search_space.append(nd)

            if len(twochoice_search_space) > 0:
                while srv1 == srv0:
                    srv1 = twochoice_search_space[np.random.randint(len(twochoice_search_space))]
                    #srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

        #if len(file_sets[rqstd_file]) > 1:
        #    while srv1 == srv0:
        #        srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

        # Implement power of two choices
#        print(srv0)
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

    print('The simulator 3 is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num

#    print(loads)
#    print(maxload)
#    print(total_cost)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost}