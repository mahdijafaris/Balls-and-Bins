# This file simulates the randomly selection of the server.
# The one choice and two choices are both implemented
# in this file that runs Simulator1 and Simulator2.

from __future__ import division
import math
#import matplotlib.pyplot as plt
#import networkx as nx
from multiprocessing import Pool
import sys
import numpy as np
import scipy.io as sio
import time
#import simplejson as json
#import csv
#import string
#from BallsBins import *
#from BallsBins.Server import Server
from BallsBins.Simulator_Torus import *


#--------------------------------------------------------------------
#log = math.log
#sqrt = math.sqrt

#--------------------------------------------------------------------
# Simulation parameters

# Choose the simulator. It can be the following values:
# 'OneChoice'
# 'TwoChoices'
#simulator = 'OneChoice'
simulator = 'TwoChoices'

# Base part of the output file name
base_out_filename = 'CacheSzVar'

# Pool size for parallel processing
pool_size = 2

# Number of runs for computing average values. It is more efficient that num_of_runs be a multiple of pool_size
num_of_runs = 4

# Number of servers
srv_num = 2025

# Number of requests
req_num = srv_num

# Cache increment step size
cache_step_sz = 20

# Total number of files in the system
file_num = 200

# The list of cache sizes that will be used in the simulation
cache_range = range(1, 20) + range(20, 200, cache_step_sz)
cache_range = [5, 19]

# The graph structure of the network
# It can be:
# 'Lattice' for square lattice graph. For the lattice the graph size should be perfect square.
# 'RGG' for random geometric graph. The RGG is generate over a unit square or unit cube.
#graph_type = 'Lattice'
graph_type = 'RGG'

# The parameters of the selected random graph
# It is always should be defined. However, for some graphs it may not be used.
graph_param = {'rgg_radius' : sqrt(5 / 4 * log(srv_num)) / sqrt(srv_num)} # RGG radius for random geometric graph.

# The distribution of file placement in nodes' caches
# It can be:
# 'Uniform' for uniform placement.
# 'Zipf' for zipf distribution.
placement_dist = 'Uniform'
#placement_dist = 'Zipf'

# The parameters of the placement distribution
place_dist_param = {'gamma' : 1.0}  # For Zipf distribution where 0 < gamma < infty


#--------------------------------------------------------------------
if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    t_start = time.time()

    rslt_maxload = np.zeros((len(cache_range), 1+num_of_runs))
    rslt_avgcost = np.zeros((len(cache_range), 1+num_of_runs))
    rslt_outage = np.zeros((len(cache_range), 1+num_of_runs))
    for i, cache_sz in enumerate(cache_range):
        params = [(srv_num, req_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param)
                  for itr in range(num_of_runs)]
        print(params)
        if simulator == 'OneChoice':
            rslts = pool.map(simulator_onechoice, params)
#            rslts = map(Simulator1, params)
        elif simulator == 'TwoChoices':
            rslts = pool.map(simulator_twochoice, params)
        else:
            print('Error: an invalid simulator!')
            sys.exit()

        for j,rslt in enumerate(rslts):
            rslt_maxload[i, j + 1] = rslt['maxload']
            rslt_avgcost[i, j + 1] = rslt['avgcost']
            rslt_outage[i, j + 1] = rslt['outage']
#                tmpmxld = tmpmxld + rslt['maxload']
#                tmpavgcst = tmpavgcst + rslt['avgcost']
            
        rslt_maxload[i, 0] = cache_sz
        rslt_avgcost[i, 0] = cache_sz
        rslt_outage[i, 0] = cache_sz
#            result[i,1] = tmpmxld/num_of_runs
#            result[i,2] = tmpavgcst/num_of_runs


    t_end = time.time()
    print("The runtime is {}".format(t_end-t_start))

    # Write the results to a matlab .mat file
    if placement_dist == 'Uniform':
        sio.savemat(base_out_filename+'_{}_{}_{}_sn={}_fn={}_itr={}.mat'.\
            format(graph_type, placement_dist, simulator, srv_num, file_num, num_of_runs),\
            {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})
    elif placement_dist == 'Zipf':
        sio.savemat(base_out_filename+'_{}_{}_gamma={}_{}_sn={}_fn={}_itr={}.mat'.\
            format(graph_type, placement_dist, place_dist_param['gamma'], simulator, srv_num, file_num, num_of_runs),\
            {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})


    #    plt.plot(result[:,0], result[:,1])
#    plt.plot(result[:,0], result[:,2])
#    plt.xlabel('Cache size in each server (# of files)')
#    plt.title('Random server selection methods. Number of servers = {}, number of files = {}'.format(srv_num,file_num))
#    plt.show()

    #print(result['loads'])
    #print("------")
    #print('The maximum load is {}'.format(result['maxload']))
    #print('The average request cost is {0:0}'.format(result['avgcost']))

    #fl_lst = [srvs[i].get_files_list() for i in range(n)]
    #print(fl_lst)

    print(rslt_outage)