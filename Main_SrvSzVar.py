# This file simulates the randomly selection of the server.
# The one choice and two choices are both implemented
# in this file that runs Simulator1 and Simulator2.
# Here we change the number of servers and find the average cost
# of users and maximum load of servers.
from __future__ import division
import math
#import matplotlib.pyplot as plt
#import networkx as nx
from multiprocessing import Pool
import sys
import numpy as np
import scipy.io as sio
import time
from BallsBins.Simulator import *

#--------------------------------------------------------------------
#log = math.log
#sqrt = math.sqrt

#--------------------------------------------------------------------
# Simulation parameters

# Choose the simulator. It can be the following values:
# 'OneChoice'
# 'TwoChoices'
simulator = 'OneChoice'
#simulator = 'TwoChoices'

# Base part of the output file name
base_out_filename = 'SrvSzVar'

# Pool size for parallel processing
pool_size = 4

# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 12

# Number of servers
#srv_range = [500, 1000, 2000, 5000, 7000, 10000, 20000, 50000, 70000, 100000, 200000, 500000]
#srv_range = [2025, 5041, 7056, 10000, 20164, 50176, 70225, 100489]
srv_range = [25, 100, 225, 400, 625, 900, 1600, 2500]
#srv_range = [225, 324, 625, 900, 1225, 1600, 2025, 3025, 4096, 5041]

# Cache size of each server (expressed in number of files)
cache_sz = 10

# Total number of files in the system
file_num = 20

# The graph structure of the network
# It can be:
# 'Lattice' for square lattice graph. For the lattice the graph size should be perfect square.
# 'RGG' for random geometric graph. The RGG is generate over a unit square or unit cube.
#graph_type = 'Lattice'
graph_type = 'RGG'

# The parameters of the selected random graph
# It is always should be defined. However, for some graphs it may not be used.
graph_param = {'rgg_radius' : 0} # RGG radius for random geometric graph.
                                    # For SrvSzVar RGG radius will be determined later.

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

    rslt_maxload = np.zeros((len(srv_range), 1 + num_of_runs))
    rslt_avgcost = np.zeros((len(srv_range), 1 + num_of_runs))
    rslt_outage = np.zeros((len(srv_range), 1 + num_of_runs))
    for i, srv_num in enumerate(srv_range):
        if graph_type == 'RGG': # if the graph is random geometric graph (RGG)
            graph_param = {'rgg_radius': sqrt(5 / 4 * log(srv_num)) / sqrt(srv_num)} # if the graph is random geometric graph (RGG)
        req_num = srv_num
        params = [(srv_num, req_num, cache_sz, file_num, graph_type, graph_param, placement_dist, place_dist_param)
                  for itr in range(num_of_runs)]
        print(params)
        if simulator == 'OneChoice':
            rslts = pool.map(simulator_onechoice, params)
        elif simulator == 'TwoChoices':
            rslts = pool.map(simulator_twochoice, params)
        else:
            print('Error: an invalid simulator!')
            sys.exit()

        for j, rslt in enumerate(rslts):
            rslt_maxload[i, j + 1] = rslt['maxload']
            rslt_avgcost[i, j + 1] = rslt['avgcost']
            rslt_outage[i, j + 1] = rslt['outage']
            #tmpmxld = tmpmxld + rslt['maxload']
            #tmpavgcst = tmpavgcst + rslt['avgcost']

        rslt_maxload[i, 0] = srv_num
        rslt_avgcost[i, 0] = srv_num
        rslt_outage[i, 0] = srv_num

    t_end = time.time()
    print("The runtime is {}".format(t_end-t_start))

    # Write the results to a matlab .mat file
    if placement_dist == 'Uniform':
        sio.savemat(base_out_filename + '_{}_{}_{}_fn={}_cs={}_itr={}.mat'.\
            format(graph_type, placement_dist, simulator, file_num, cache_sz, num_of_runs),
            {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage': rslt_outage})
    elif placement_dist == 'Zipf':
        sio.savemat(base_out_filename + '_{}_{}_gamma={}_{}_fn={}_cs={}_itr={}.mat'.\
            format(graph_type, placement_dist, place_dist_param['gamma'], simulator, file_num, cache_sz, num_of_runs),
            {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage': rslt_outage})



#    if simulator == 'one choice':
#        sio.savemat(base_out_filename + '_{}_fn={}_cs={}_itr={}.mat'.format(simulator, file_num, cache_sz, num_of_runs),
#                    {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage':rslt_outage})
#    elif simulator == 'two choice':
#        sio.savemat(base_out_filename + '_two_choice_' + 'fn={}_cs={}_itr={}.mat'.format(file_num, cache_sz, num_of_runs),
#                    {'maxload': rslt_maxload, 'avgcost': rslt_avgcost, 'outage':rslt_outage})





#    if simulator == 'one choice':
#        np.savetxt(base_out_filename+'_sim1_'+'fn={}_cs={}_itr={}.txt'.format(file_num,cache_sz,num_of_runs), result, delimiter=',')
#    elif simulator == 'two choice':
#        np.savetxt(base_out_filename+'_sim2_'+'fn={}_cs={}_itr={}.txt'.format(file_num,cache_sz,num_of_runs), result, delimiter=',')

#    plt.plot(result[:,0], result[:,1])
#    plt.plot(result[:,0], result[:,2])
#    plt.xlabel('Cache size in each server (# of files)')
#    plt.title('Random server selection methods. Number of servers = {}, number of files = {}'.format(srv_num,file_num))
#    plt.show()

    #print(result['loads'])
    #print("------")
    #print('The maximum load is {}'.format(result['maxload']))
    #print('The average request cost is {0:0}'.format(result['avgcost']))


    print(rslt_outage)