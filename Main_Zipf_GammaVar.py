# This file simulates the randomly selection of the server.
# The "one choice" and "two choices" scheme are both implemented.
# Here we derive "maximum load" and "average comm. cost" for Zipf
# distribution versus Zipf parameter gamma (0 \le gamma \le infty).

from __future__ import division
import math
# import matplotlib.pyplot as plt
# import networkx as nx
from multiprocessing import Pool
import sys
import numpy as np
import scipy.io as sio
import time
# import simplejson as json
# import csv
# import string
# from BallsBins import *
# from BallsBins.Server import Server
from BallsBins.Simulator import *


# --------------------------------------------------------------------
# log = math.log
# sqrt = math.sqrt

# --------------------------------------------------------------------
# Simulation parameters

# Choose the simulator. It can be the following values:
# 'OneChoice'
# 'TwoChoices'
simulator = 'OneChoice'
# simulator = 'TwoChoices'

# Base part of the output file name
base_out_filename = 'ZipfGammaVar'

# Pool size for parallel processing
pool_size = 4

# Total number of runs for computing the average values.
# It is more efficient that num_of_runs be a multiple of pool_size
num_of_runs = 10

# Number of servers
srv_num = 625#5041

# Number of requests
req_num = srv_num

# Cache size of each server (expressed in number of files)
cache_sz = 200

# Total number of files in the system
file_num = 500

# The list of cache sizes that will be used in the simulation
#cache_range = range(1, 20) + range(20, 200, cache_step_sz)
#cache_range = [5, 19]

# The graph structure of the network
# It can be:
# 'Lattice' for square lattice graph. For the lattice the graph size should be perfect square.
# 'RGG' for random geometric graph. The RGG is generate over a unit square or unit cube.
# 'BarabasiAlbert' for Barabasi Albert random graph. It takes two parameters: # of nodes and # of edges
#       to attach from a new node to existing nodes
#graph_type = 'Lattice'
#graph_type = 'RGG'
graph_type = 'BarabasiAlbert'

# The parameters of the selected random graph
# It is always should be defined. However, for some graphs it may not be used.
graph_param = {'rgg_radius' : sqrt(5 / 4 * log(srv_num)) / sqrt(srv_num)} # RGG radius for random geometric graph.
graph_param = {'num_edges' : 1} # For Barbasi Albert random graphs.

# The distribution of file placement in nodes' caches
# It can be:
# 'Uniform' for uniform placement, or
# 'Zipf' for Zipf placement. We have to determine the parameter 'gamma' for this distribution in 'place_dist_param'.
# placement_dist = 'Uniform'
# But here we have to choose Zipf!
placement_dist = 'Zipf'

# The list of Zipf parameters for simulation
gamma_range = [0, 0.1, 0.5, 1.0, 1.5, 2.0]
#gamma_range = [1.0]

# The parameters of the placement distribution
#place_dist_param = {'gamma': 1.0}  # For Zipf distribution where 0 < gamma < infty


# --------------------------------------------------------------------
if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    t_start = time.time()

    rslt_maxload = np.zeros((len(gamma_range), 1 + num_of_runs))
    rslt_avgcost = np.zeros((len(gamma_range), 1 + num_of_runs))
    rslt_outage = np.zeros((len(gamma_range), 1 + num_of_runs))
    for i, gm in enumerate(gamma_range):
        place_dist_param = {'gamma' : gm}
        params = [(srv_num, req_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param)
                  for itr in range(num_of_runs)]
        print(params)
        if simulator == 'OneChoice':
            rslts = pool.map(simulator_onechoice, params)
        # rslts = map(Simulator1, params)
        elif simulator == 'TwoChoice':
            rslts = pool.map(simulator_twochoice, params)
        else:
            print('Error: an invalid simulator!')
            sys.exit()

        for j, rslt in enumerate(rslts):
            rslt_maxload[i, j + 1] = rslt['maxload']
            rslt_avgcost[i, j + 1] = rslt['avgcost']
            rslt_outage[i, j + 1] = rslt['outage']
        # tmpmxld = tmpmxld + rslt['maxload']
        #                tmpavgcst = tmpavgcst + rslt['avgcost']

        rslt_maxload[i, 0] = gm
        rslt_avgcost[i, 0] = gm
        rslt_outage[i, 0] = gm
    # result[i,1] = tmpmxld/num_of_runs
    #            result[i,2] = tmpavgcst/num_of_runs

    t_end = time.time()
    print("The runtime is {}".format(t_end - t_start))

    # Write the results to a matlab .mat file
    if placement_dist == 'Uniform':
        sio.savemat(base_out_filename+'_{}_{}_{}_sn={}_fn={}_cs={}_itr={}.mat'.\
            format(graph_type, placement_dist, simulator, srv_num, file_num, cache_sz, num_of_runs), \
            {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage': rslt_outage})
    elif placement_dist == 'Zipf':
        sio.savemat(base_out_filename+'_{}_{}_{}_sn={}_fn={}_cs={}_itr={}.mat'.\
            format(graph_type, placement_dist, simulator, srv_num, file_num, cache_sz, num_of_runs), \
            {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage': rslt_outage})


    #    plt.plot(result[:,0], result[:,1])
    #    plt.plot(result[:,0], result[:,2])
    #    plt.xlabel('Cache size in each server (# of files)')
    #    plt.title('Random server selection methods. Number of servers = {}, number of files = {}'.format(srv_num,file_num))
    #    plt.show()

    # print(result['loads'])
    # print("------")
    # print('The maximum load is {}'.format(result['maxload']))
    # print('The average request cost is {0:0}'.format(result['avgcost']))

    # fl_lst = [srvs[i].get_files_list() for i in range(n)]
    # print(fl_lst)

    print(rslt_outage)