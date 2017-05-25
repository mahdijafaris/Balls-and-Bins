# This file implements 3 versions of balls and bins simulator but the
# functions are specialized only for Torus.
# The 3 functions are: simulator1_torus, simulator2_torus, simulator3_torus
#
from __future__ import division
import math
import sys
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
#import string
#from BallsBins import *
from BallsBins.Statistic import bounded_zipf
from BallsBins.Server import Server
from BallsBins.Graph import Gen2DLattice
from BallsBins.Graph import *


#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt


#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# This function simulates the randomly selection of the server
# but there is no power of two choices.
# This function is specialized for a Torus graph.
def simulator_onechoice(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system

    np.random.seed()  # to prevent all the instances produce the same results!

    srv_num, req_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param = params

    print('The "one choice" simulator is starting with parameters:')
    print('# of Servers = {}, # of Reqs = {}, # of Files = {}, Cache Size = {}, \
            Net. Topology = {}, Placement Dist. = {}, Plc. Dist. Param. = {}'\
            .format(srv_num, req_num, file_num, cache_sz, graph_type, placement_dist, place_dist_param))

    # Check the validity of parameters
    if cache_sz > file_num:
        print("Error: The cache size is larger that number of files!")
        sys.exit()

    if graph_type == 'Lattice':
        side = sqrt(srv_num)
        if not side.is_integer():
            print("Error: the size of lattice is not perfect square!")
            sys.exit()
        shortest_path_matrix = all_shortest_path_length_torus(srv_num)
#        print('Start generating a square lattice graph with {} nodes...'.format(srv_num))
#        G = Gen2DLattice(srv_num)
#        print('Succesfully generates a square lattice graph with {} nodes...'.format(srv_num))
    elif graph_type == 'RGG': # if the graph is random geometric graph (RGG)
        rgg_radius = graph_param['rgg_radius']
        # Generate a random geometric graph.
        print('Start generating a random geometric graph with {} nodes...'.format(srv_num))
        conctd = False
        while not conctd:
            G = nx.random_geometric_graph(srv_num, rgg_radius)
            conctd = nx.is_connected(G)
        print('Succesfully generates a connected random geometric graph with {} nodes...'.format(srv_num))
        all_sh_len = nx.all_pairs_shortest_path_length(G)
        shortest_path_matrix = np.array([all_sh_len[i][j] for i in all_sh_len.keys() for j in all_sh_len[i].keys()],\
                                        dtype=np.int32)
        shortest_path_matrix = shortest_path_matrix.reshape(srv_num, srv_num)
    else:
        print("Error: the graph type is not known!")
        sys.exit()
    # Draw the graph
    #nx.draw(G)
    #plt.show()

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # Cache placement at servers according to file popularity distribution
    #
    # file_sets = List of sets of servers containing each file
    # list_cached_files = List of all cached files at the end of placement process
    srvs, file_sets, list_cached_files = \
        srv_cache_placement(srv_num, file_num, cache_sz, placement_dist, place_dist_param, srvs)

    # ---------------------------------------------------------------
    # Main loop of the simulator.
    # ---------------------------------------------------------------
    # We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    print('The "one choice" simulator core is starting...')

    total_cost = 0  # Measured in number of hops.
    outage_num = 0  # Measure the # of outage events, i.e., the # of events that the requested
                    # file has not cached in the whole network.

    # Generate all the random incoming servers
    incoming_srv_lst = np.random.randint(srv_num, size=req_num)

    # Generate all the random requests
    if placement_dist == 'Uniform':
        rqstd_file_lst = np.random.randint(file_num, size=req_num)
    elif placement_dist == 'Zipf':
        rqstd_file_lst = bounded_zipf(file_num, place_dist_param['gamma'], req_num)

    for i in range(req_num):
        #print(i)
        incoming_srv = incoming_srv_lst[i] # Random incoming server

        rqstd_file = rqstd_file_lst[i] # Random requested file

        if rqstd_file in list_cached_files:
            if incoming_srv in file_sets[rqstd_file]:
                srv0 = incoming_srv
            else:
                # Find the nearest server that has the requested file
                #all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)
                #all_sh_path_len_G = shortest_path_length_torus(srv_num, incoming_srv)
                dmin = 2*srv_num # some large number!
                for nd in file_sets[rqstd_file]:
                    #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                    #d = all_sh_path_len_G[nd]
                    d = shortest_path_matrix[incoming_srv, nd]
                    if d < dmin:
                        dmin = d
                        srv0 = nd
                total_cost = total_cost + dmin
#                srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]
#                total_cost = total_cost + nx.shortest_path_length(G, source=incoming_srv, target=srv0)

            # Implement random placement without considering loads
            srvs[srv0].add_load()
        else:
            outage_num += 1

    print('The "one choice" simulator is done.')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost / srv_num
    outage = outage_num / srv_num

#    print(loads)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost, 'outage':outage}


#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# This function is the core implementation of power of two choices.
def simulator_twochoice(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system

    np.random.seed()  # to prevent all the instances produce the same results!

    #srv_num, req_num, cache_sz, file_num, graph_type, placement_dist, place_dist_param = params
    srv_num, req_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param = params

    print('The "two choices" simulator is starting with parameters:')
    print('# of Servers = {}, # of Reqs = {}, # of Files = {}, Cache Size = {},\
            Net. Topology = {}, Placement Dist. = {}, Plc. Dist. Param. = {}'\
            .format(srv_num, req_num, file_num, cache_sz, graph_type, placement_dist, place_dist_param))

    # Check the validity of parameters
    if cache_sz > file_num:
        print("Error: The cache size is larger that number of files!")
        sys.exit()

    if graph_type == 'Lattice':
        side = sqrt(srv_num)
        if not side.is_integer():
            print("Error: the size of lattice is not perfect square!")
            sys.exit()
        shortest_path_matrix = all_shortest_path_length_torus(srv_num)
        #        print('Start generating a square lattice graph with {} nodes...'.format(srv_num))
        #        G = Gen2DLattice(srv_num)
        #        print('Succesfully generates a square lattice graph with {} nodes...'.format(srv_num))
    elif graph_type == 'RGG':  # if the graph is random geometric graph (RGG)
        rgg_radius = graph_param['rgg_radius']
        # Generate a random geometric graph.
        print('Start generating a random geometric graph with {} nodes...'.format(srv_num))
        conctd = False
        while not conctd:
            G = nx.random_geometric_graph(srv_num, rgg_radius)
            conctd = nx.is_connected(G)
        print('Succesfully generates a connected random geometric graph with {} nodes...'.format(srv_num))
        all_sh_len = nx.all_pairs_shortest_path_length(G)
        shortest_path_matrix = np.array([all_sh_len[i][j] for i in all_sh_len.keys() for j in all_sh_len[i].keys()], \
                                        dtype=np.int32)
        shortest_path_matrix = shortest_path_matrix.reshape(srv_num, srv_num)
    else:
        print("Error: the graph type is not known!")
        sys.exit()
        # Draw the graph
        # nx.draw(G)
        # plt.show()

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # Cache placement at servers according to file popularity distribution
    #
    # file_sets = List of sets of servers containing each file
    # list_cached_files = List of all cached files at the end of placement process
    srvs, file_sets, list_cached_files = \
        srv_cache_placement(srv_num, file_num, cache_sz, placement_dist, place_dist_param, srvs)

    # ---------------------------------------------------------------
    # Main loop of the simulator.
    # ---------------------------------------------------------------
    # We throw n ball requests into the servers.
    # Each request randomly pick a server and a file.
    print('The "two choices" simulator core is starting...')

    total_cost = 0  # Measured in number of hops.
    outage_num = 0  # Measure the # of outage events, i.e., the # of events that the requested
                    # file has not cached in the whole network.

    # Generate all the random incoming servers
    incoming_srv_lst = np.random.randint(srv_num, size=req_num)

    # Generate all the random requests
    if placement_dist == 'Uniform':
        rqstd_file_lst = np.random.randint(file_num, size=req_num)
    elif placement_dist == 'Zipf':
        rqstd_file_lst = bounded_zipf(file_num, place_dist_param['gamma'], req_num)

#    print(len(rqstd_file_lst))
#    print(len(incoming_srv_lst))

    for i in range(req_num):
        #print(i)
        incoming_srv = incoming_srv_lst[i] # Random incoming server

        rqstd_file = rqstd_file_lst[i] # Random requested file

        #print(len(list_cached_files))

        if rqstd_file in list_cached_files:
#            all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)
            #all_sh_path_len_G = shortest_path_length_torus(srv_num, incoming_srv)
            if incoming_srv in file_sets[rqstd_file]:
                srv0 = incoming_srv
            else:
                # Find the nearest server that has the requested file
                dmin = 2*srv_num # some large number!
                for nd in file_sets[rqstd_file]:
                    #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                    #d = all_sh_path_len_G[nd]
                    d = shortest_path_matrix[incoming_srv, nd]
                    if d < dmin:
                        dmin = d
                        srv0 = nd
#                srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]

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
                #total_cost += all_sh_path_len_G[srv1]
                total_cost += shortest_path_matrix[incoming_srv, srv1]
            elif load0 < load1:
                srvs[srv0].add_load()
                if srv0 != incoming_srv:
                    #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                    #total_cost += all_sh_path_len_G[srv0]
                    total_cost += shortest_path_matrix[incoming_srv, srv0]
            elif np.random.randint(2) == 0:
                srvs[srv0].add_load()
                if srv0 != incoming_srv:
                    #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                    #total_cost += all_sh_path_len_G[srv0]
                    total_cost += shortest_path_matrix[incoming_srv, srv0]
            else:
                srvs[srv1].add_load()
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
                #total_cost += all_sh_path_len_G[srv1]
                total_cost += shortest_path_matrix[incoming_srv, srv1]
        else:
            outage_num +=  1


    print('The "two choices" simulator is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost/srv_num
    outage = outage_num / srv_num

#    print(loads)
#    print(maxload)
#    print(total_cost)

    return {'loads':loads, 'maxload':maxload, 'avgcost':avgcost, 'outage':outage}


#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# This function simulates the trade-off between 'minimum
# communication cost scheme' and 'minimum load scheme'.
#
# Here we implement the power of two choices. However we change the
# radius of search for finding two bins. By changing this radius, we
# will get different trade-offs.
def simulator_tradeoff(params):
    # Simulation parameters
    # srv_num: Number of servers
    # cache_sz: Cache size of each server (expressed in number of files)
    # file_num: Total number of files in the system
    # graph_type: Topology of network
    # graph_param: Parameters for generating network topology
    # placement_dist: File library distribution
    # place_dist_param: Parameters of file library distribution
    # alpha: alpha determines the search space as follows: (1+alpha)NearestNeighborDistance

    np.random.seed()  # to prevent all the instances produce the same results!

    srv_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param, alpha = params

    print('The "Trade-off" simulator is starting with parameters:')
    print('# of Srvs = {}, # of Files = {}, Cache Size = {}, Net. Top. = {},\
            alpha = {}, Plc. Dist. = {}, Plc. Dist. Param. = {}'\
            .format(srv_num, file_num, cache_sz, graph_type, alpha, placement_dist, place_dist_param))

    # Check the validity of parameters
    if cache_sz > file_num:
        print("Error: The cache size is larger that number of files!")
        sys.exit()

    if graph_type == 'Lattice':
        side = sqrt(srv_num)
        if not side.is_integer():
            print("Error: the size of lattice is not perfect square!")
            sys.exit()
        shortest_path_matrix = all_shortest_path_length_torus(srv_num)
        #        print('Start generating a square lattice graph with {} nodes...'.format(srv_num))
        #        G = Gen2DLattice(srv_num)
        #        print('Succesfully generates a square lattice graph with {} nodes...'.format(srv_num))
    elif graph_type == 'RGG':  # if the graph is random geometric graph (RGG)
        rgg_radius = graph_param['rgg_radius']
        # Generate a random geometric graph.
        print('Start generating a random geometric graph with {} nodes...'.format(srv_num))
        conctd = False
        while not conctd:
            G = nx.random_geometric_graph(srv_num, rgg_radius)
            conctd = nx.is_connected(G)
        print('Succesfully generates a connected random geometric graph with {} nodes...'.format(srv_num))
        all_sh_len = nx.all_pairs_shortest_path_length(G)
        shortest_path_matrix = np.array([all_sh_len[i][j] for i in all_sh_len.keys() for j in all_sh_len[i].keys()], \
                                        dtype=np.int32)
        shortest_path_matrix = shortest_path_matrix.reshape(srv_num, srv_num)
    else:
        print("Error: the graph type is not known!")
        sys.exit()
        # Draw the graph
        # nx.draw(G)
        # plt.show()

    # Create 'srv_num' servers from the class server
    srvs = [Server(i) for i in range(srv_num)]

    # Cache placement at servers according to file popularity distribution
    #
    # file_sets = List of sets of servers containing each file
    # list_cached_files = List of all cached files at the end of placement process
    srvs, file_sets, list_cached_files = \
        srv_cache_placement(srv_num, file_num, cache_sz, placement_dist, place_dist_param, srvs)


    # List of sets of servers containing each file. The list is enumerate by the
    # file index and for each file we have a list that contains the servers cached that file.
#    file_sets = [[] for i in range(file_num)]

#    if placement_dist == 'Uniform':
        # Randomly places cache_sz files in each servers
#        print('Start randomly placing {} files in each server with Uniform dist.'.format(cache_sz))
        # First put randomly one copy of each file in a subset of servers (assuming file_num =< srv_num)
#        lst = np.random.permutation(srv_num)[0:file_num]
#        for i, s in enumerate(lst):
#            file_sets[i].append(s)
#            srvs[s].set_files_list([i])
        # Then fills the rest of empty cache places
#        for s in range(srv_num):
            #print(s)
#            srvlst = srvs[s].get_files_list()
#            tmp_lst = np.random.permutation(file_num)[0:cache_sz - len(srvlst)]
#            srvs[s].set_files_list(srvlst.extend(tmp_lst))
#            for j in range(len(tmp_lst)):
#                if s not in file_sets[tmp_lst[j]]:
#                    file_sets[tmp_lst[j]].append(s)
#        print('Done with randomly placing {} files in each server with Uniform dist.'.format(cache_sz))
#    elif placement_dist == 'Zipf':
        # Randomly places cache_sz files in each servers with Zipf dist.
#        print('Start randomly placing {} files in each server with Zipf dist.'.format(cache_sz))
#        gamma = place_dist_param['gamma']  # Parameter of Zipf distribution.
#        list_chached_files = []  # List of all cached files at the end of placement process

#        for s in np.arange(srv_num, dtype=np.int32):
#            tmp_lst = bounded_zipf(file_num, gamma, cache_sz)
#            srvs[s].set_files_list(tmp_lst)
#            for j in np.arange(len(tmp_lst), dtype=np.int32):
#                if s not in file_sets[tmp_lst[j]]:
#                    file_sets[tmp_lst[j]].append(s)
#                if tmp_lst[j] not in list_chached_files:
#                    list_chached_files.append(tmp_lst[j])
        #print(list_chached_files)
#        print('Done with randomly placing {} files in each server with Zipf dist.'.format(cache_sz))

    # Main loop of the simulator.
    # We throw n balls requests into the servers.
    # Each request randomly pick a server and a file.
    # Then we apply the power of two choices scheme but up to some radius from the requsting
    # node.
    print('The "Trade-off" simulator core is starting...')
#          with parameters: sn={}, cs={}, fn={}, graph_type={}, alpha={}'\
#          .format(srv_num, cache_sz, file_num, graph_type, alpha))

    total_cost = 0  # Measured in number of hops.
    outage_num = 0  # Measure the # of outage events, i.e., the # of events that the requested
                    # file has not cached in the whole network.

    # Generate all the random incoming servers
    incoming_srv_lst = np.random.randint(srv_num, size=srv_num)

    # Generate all the random requests
    if placement_dist == 'Uniform':
        rqstd_file_lst = np.random.randint(file_num, size=srv_num)
    elif placement_dist == 'Zipf':
        rqstd_file_lst = bounded_zipf(file_num, place_dist_param['gamma'], srv_num)

    for i in range(srv_num):
        #print(i)
        incoming_srv = incoming_srv_lst[i] # Random incoming server

        rqstd_file = rqstd_file_lst[i] # Random requested file

        if rqstd_file in list_cached_files:
            # Find the shortest path from requesting nodes to all other nodes
            #all_sh_path_len_G = nx.shortest_path_length(G, source=incoming_srv)
            #all_sh_path_len_G = shortest_path_length_torus(srv_num, incoming_srv)

            # Find the nearest server that has the requested file
#            print(file_sets[rqstd_file])
#            print(type(file_sets[rqstd_file][0]))
#            print(list(file_sets[rqstd_file]))
            nearest_neighbor = []
            srv_lst_for_this_request_excld_incom_srv = list(file_sets[rqstd_file])
            if incoming_srv in file_sets[rqstd_file]:
                srv_lst_for_this_request_excld_incom_srv.remove(incoming_srv)
#            print(srv_lst_for_this_request_excld_incom_srv)
            if len(srv_lst_for_this_request_excld_incom_srv) > 0:
                dmin = 2*srv_num # some large number, eg, larger that the graph diameter!
                for nd in srv_lst_for_this_request_excld_incom_srv:
                    #d = nx.shortest_path_length(G, source=incoming_srv, target=nd)
                    #dtmp = all_sh_path_len_G[nd]
                    dtmp = shortest_path_matrix[incoming_srv, nd]
                    if dtmp < dmin:
                        dmin = dtmp
                        nearest_neighbor = nd
#            print(file_sets[rqstd_file])
#            print(srv_lst_for_this_request_excld_incom_srv)

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
                    if shortest_path_matrix[incoming_srv, nd] <= (1+alpha)*dmin and nd != srv0:
                        twochoice_search_space.append(nd)

                if len(twochoice_search_space) > 0:
                    while srv1 == srv0:
                        srv1 = twochoice_search_space[np.random.randint(len(twochoice_search_space))]
                        #srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

            #if len(file_sets[rqstd_file]) > 1:
            #    while srv1 == srv0:
            #        srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file]))]

            # Implement power of two choices
#            print(srv0)
            load0 = srvs[srv0].get_load()
            load1 = srvs[srv1].get_load()
            if load0 > load1:
                srvs[srv1].add_load()
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
                #total_cost += all_sh_path_len_G[srv1]
                total_cost += shortest_path_matrix[incoming_srv, srv1]
            elif load0 < load1:
                srvs[srv0].add_load()
                if srv0 != incoming_srv:
                    #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                    #total_cost += all_sh_path_len_G[srv0]
                    total_cost += shortest_path_matrix[incoming_srv, srv0]
            elif np.random.randint(2) == 0:
                srvs[srv0].add_load()
                if srv0 != incoming_srv:
                    #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv0)
                    #total_cost += all_sh_path_len_G[srv0]
                    total_cost += shortest_path_matrix[incoming_srv, srv0]
            else:
                srvs[srv1].add_load()
                #total_cost += nx.shortest_path_length(G, source=incoming_srv, target=srv1)
                #total_cost += all_sh_path_len_G[srv1]
                total_cost += shortest_path_matrix[incoming_srv, srv1]
        else:
            outage_num +=  1


    print('The "Trade-off" simulator is done.')
#    print('------------------------------')

    # At the end of simulation, find maximum load, etc.
    loads = [srvs[i].get_load() for i in range(srv_num)]
    maxload = max(loads)
    avgcost = total_cost / srv_num
    outage = outage_num / srv_num

#    print(loads)
#    print(maxload)
#    print(total_cost)

    return {'loads': loads, 'maxload': maxload, 'avgcost': avgcost, 'outage': outage}

#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# This function randomly places library files into the server caches.
#
# Input:
# srv_num = number of servers
# file_num = number of files in the library
# cache_sz = size of cache in each server
# placement_dist = the file popularity distribution
#
# Return:
#
def srv_cache_placement(srv_num, file_num, cache_sz, placement_dist, place_dist_param, srvs):

    # List of sets of servers containing each file. The list is enumerate by the
    # file index and for each file we have a list that contains the servers cached that file.
    file_sets = [[] for i in range(file_num)]

    # List of all cached files at the end of placement process
    list_cached_files = []

    if placement_dist == 'Uniform':
        # Randomly places cache_sz files in each servers
        print('Start randomly placing {} files in each server with Uniform dist.'.format(cache_sz))
        # First put randomly one copy of each file in a subset of servers (assuming file_num =< srv_num)
        lst = np.random.permutation(srv_num)[0:file_num]
        for i, s in enumerate(lst):
            file_sets[i].append(s)
            srvs[s].set_files_list([i])
            list_cached_files.append(i)
        # Then fills the rest of empty cache places
        for s in range(srv_num):
            #print(s)
            srvlst = srvs[s].get_files_list()
            tmp_lst = np.random.permutation(file_num)[0:cache_sz - len(srvlst)]
            srvs[s].set_files_list(srvlst.extend(tmp_lst))
            for j in range(len(tmp_lst)):
                if s not in file_sets[tmp_lst[j]]:
                    file_sets[tmp_lst[j]].append(s)
        print('Done with randomly placing {} files in each server with Uniform dist.'.format(cache_sz))
    elif placement_dist == 'Zipf':
        # Randomly places cache_sz files in each servers with Zipf dist.
        gamma = place_dist_param['gamma']  # Parameter of Zipf distribution.
        print('Start randomly placing {} files in each server according to Zipf dist. with gamma={}'.\
              format(cache_sz, gamma))

        for s in np.arange(srv_num, dtype=np.int32):
            tmp_lst = bounded_zipf(file_num, gamma, cache_sz)
            srvs[s].set_files_list(tmp_lst)
            for j in np.arange(len(tmp_lst), dtype=np.int32):
                if s not in file_sets[tmp_lst[j]]:
                    file_sets[tmp_lst[j]].append(s)
                if tmp_lst[j] not in list_cached_files:
                    list_cached_files.append(tmp_lst[j])
        #print(list_chached_files)
        print('Done with randomly placing {} files in each server with Zipf dist.'.format(cache_sz))

    #print(list_cached_files)

    return srvs, file_sets, list_cached_files