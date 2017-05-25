# This file simulates the randomly selection of the server.
#
# The one choice and two choices are both implemented
# in this file that runs Simulator1 and Simulator2.
#
# Here, the number of requests (m in our paper) is changed
# and the maximum load vs average load will be investigated.


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
#from BallsBins.Simulator1 import Simulator1_lowmem
#from BallsBins.Simulator2 import Simulator2_torus
#from BallsBins.Simulator2 import Simulator2_lowmem


#--------------------------------------------------------------------
#log = math.log
#sqrt = math.sqrt

#--------------------------------------------------------------------
# Simulation parameters

# Choose the simulator. It can be the following values:
# 'one choice'
# 'two choice'
#simulator = 'one choice'
simulator = 'two choice'

# Base part of the output file name
base_out_filename = 'ReqNumVar'

# Pool size for parallel processing
pool_size = 2

# Number of runs for computing average values. It is more efficient that num_of_runs be a multiple of pool_size
num_of_runs = 200

# Number of servers
srv_num = 2025

# Cache size of each server (expressed in number of files)
cache_sz = 10

# Total number of files in the system
file_num = 200

# The graph structure of the network
# It can be:
# 'Lattice' for square lattice graph. For the lattice the graph size should be perfect square.
# 'RGG' for random geometric graph.
graph_type = 'Lattice'

# The distribution of file placement in nodes' caches
# It can be:
# 'Uniform' for uniform placement.
# 'Zipf' for Zipf placement. We have to determine the parameter 'gamma' for this distribution in 'place_dist_param'.
placement_dist = 'Uniform'
#placement_dist = 'Zipf'

# The parameters of the placement distribution
place_dist_param = {'gamma' : 0.0}  # For Zipf distribution where 0 < gamma < infty
#place_dist_param = {}

# The set of request numbers
req_num_set = [1, 100, 500, 1000, 1500, 1800, 2025, 2300, 2800, 3500, 5000, 8000]
#req_num_set = [20]

#--------------------------------------------------------------------
if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    t_start = time.time()

    rslt_maxload = np.zeros((len(req_num_set), 1+num_of_runs))
    rslt_avgcost = np.zeros((len(req_num_set), 1+num_of_runs))
    rslt_outage = np.zeros((len(req_num_set), 1+num_of_runs))
    for i, req_num in enumerate(req_num_set):
        params = [(srv_num, req_num, cache_sz, file_num, graph_type, placement_dist, place_dist_param)
                  for itr in range(num_of_runs)]
        print(params)
        if simulator == 'one choice':
            rslts = pool.map(simulator_onechoice, params)
#            rslts = map(Simulator1, params)
        elif simulator == 'two choice':
            rslts = pool.map(simulator_twochoice_torus, params)
        else:
            print('Error: an invalid simulator!')
            sys.exit()

        for j,rslt in enumerate(rslts):
            rslt_maxload[i, j + 1] = rslt['maxload']
            rslt_avgcost[i, j + 1] = rslt['avgcost']
            rslt_outage[i, j + 1] = rslt['outage']
#                tmpmxld = tmpmxld + rslt['maxload']
#                tmpavgcst = tmpavgcst + rslt['avgcost']
            
        rslt_maxload[i, 0] = req_num
        rslt_avgcost[i, 0] = req_num
        rslt_outage[i, 0] = req_num
#            result[i,1] = tmpmxld/num_of_runs
#            result[i,2] = tmpavgcst/num_of_runs


    t_end = time.time()
    print("The runtime is {}".format(t_end-t_start))

    if (simulator == 'one choice') or (simulator == 'one choice, low mem'):
        if placement_dist == 'Uniform':
            sio.savemat(base_out_filename+'_{}_one_choice_srvn={}_fn={}_cs={}_itr={}.mat'\
                        .format(placement_dist,srv_num,file_num,cache_sz,num_of_runs),\
                        {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})
        elif placement_dist == 'Zipf':
            sio.savemat(base_out_filename+'_{}_gamma={}_one_choice_srvn={}_fn={}_cs={}_itr={}.mat'\
                        .format(placement_dist,place_dist_param['gamma'],srv_num,file_num,cache_sz,num_of_runs),\
                        {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})
    elif (simulator == 'two choice') or (simulator == 'two choice, low mem'):
        if placement_dist == 'Uniform':
            sio.savemat(base_out_filename+'_{}_two_choices_srvn={}_fn={}_cs={}_itr={}.mat'\
                        .format(placement_dist,srv_num,file_num,cache_sz,num_of_runs),\
                        {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})
        elif placement_dist == 'Zipf':
            sio.savemat(base_out_filename+'_{}_gamma={}_two_choices_srvn={}_fn={}_cs={}_itr={}.mat'\
                        .format(placement_dist,place_dist_param['gamma'],srv_num,file_num,cache_sz,num_of_runs),\
                        {'maxload':rslt_maxload,'avgcost':rslt_avgcost, 'outage':rslt_outage})

    print(placement_dist)
#    if simulator == 'one choice':
#        np.savetxt(base_out_filename+'_sim1_'+'sn={}_fn={}_itr={}.txt'.format(srv_num,file_num,num_of_runs), result, delimiter=',')
#    elif simulator == 'two choice':
#        np.savetxt(base_out_filename+'_sim2_'+'sn={}_fn={}_itr={}.txt'.format(srv_num,file_num,num_of_runs), result, delimiter=',')

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