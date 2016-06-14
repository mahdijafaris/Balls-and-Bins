# This file simulates the randomly selection of the server.
# The one choice and two choices are both implemented
# in this file that runs Simulator1 and Simulator2.
from __future__ import division
import math
#import matplotlib.pyplot as plt
#import networkx as nx
from multiprocessing import Pool
import numpy as np
import scipy.io as sio
import time
#import simplejson as json
#import csv
#import string
#from BallsBins import *
#from BallsBins.Server import Server
from BallsBins.Simulator1 import Simulator1
from BallsBins.Simulator2 import Simulator2


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
base_out_filename = 'CacheSzVar'
# Pool size for parallel processing
pool_size = 2
# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 20
# Number of servers
srv_num = 200
# Cache size of each server (expressed in number of files)
#cache_sz = 2
# Cache increment step size
cache_step_sz = 10
# Total number of files in the system
file_num = 50
# The list of cache sizes that will be used in the simulation
cache_range = [1,2,3,4,5,6,7,8,9] + range(10,file_num,cache_step_sz)
# The graph structure of the network
# It can be: 'RGG' for random geometric graph, and
# 'Lattice' for square lattice graph. For the lattice the graph size should be perfect square.
graph_type = 'Lattice'

#--------------------------------------------------------------------


if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    t_start = time.time()

    if simulator == 'one choice':
        i = -1
        #result = np.zeros((len(cache_range),3))
        rslt_maxload = np.zeros((len(cache_range),1+num_of_runs))
        rslt_avgcost = np.zeros((len(cache_range),1+num_of_runs))
        for cache_sz in cache_range:
            i = i + 1
            tmpmxld = 0
            tmpavgcst = 0
            params = [(srv_num, cache_sz, file_num, graph_type) for itr in range(num_of_runs)]
            print(params)
            rslts = pool.map(Simulator1, params)
#            rslts = map(Simulator1, params)
            for j,rslt in enumerate(rslts):
                rslt_maxload[i,j+1] = rslt['maxload']
                rslt_avgcost[i,j+1] = rslt['avgcost']
#                tmpmxld = tmpmxld + rslt['maxload']
#                tmpavgcst = tmpavgcst + rslt['avgcost']
            
            rslt_maxload[i,0] = cache_sz
            rslt_avgcost[i,0] = cache_sz
#            result[i,1] = tmpmxld/num_of_runs
#            result[i,2] = tmpavgcst/num_of_runs

    elif simulator == 'two choice':
        i = -1
#        result = np.zeros((len(cache_range),3))
        rslt_maxload = np.zeros((len(cache_range),1+num_of_runs))
        rslt_avgcost = np.zeros((len(cache_range),1+num_of_runs))
        for cache_sz in cache_range:
            i = i + 1
            tmpmxld = 0
            tmpavgcst = 0
            params = [(srv_num, cache_sz, file_num, graph_type) for itr in range(num_of_runs)]
            print(params)
            rslts = pool.map(Simulator2, params)
#            rslts = map(Simulator2, params)
            #rslts = Simulator2((200,1,20))
            for j,rslt in enumerate(rslts):
                rslt_maxload[i,j+1] = rslt['maxload']
                rslt_avgcost[i,j+1] = rslt['avgcost']
#                tmpmxld = tmpmxld + rslt['maxload']
#                tmpavgcst = tmpavgcst + rslt['avgcost']

            rslt_maxload[i,0] = cache_sz
            rslt_avgcost[i,0] = cache_sz
#            result[i,1] = tmpmxld/num_of_runs
#            result[i,2] = tmpavgcst/num_of_runs

    t_end = time.time()
    print("The runtime is {}".format(t_end-t_start))

    if simulator == 'one choice':
        sio.savemat(base_out_filename+'_one_choice_'+'sn={}_fn={}_itr={}.mat'.format(srv_num,file_num,num_of_runs), {'maxload':rslt_maxload,'avgcost':rslt_avgcost})
    elif simulator == 'two choice':
        sio.savemat(base_out_filename+'_two_choice_'+'sn={}_fn={}_itr={}.mat'.format(srv_num,file_num,num_of_runs), {'maxload':rslt_maxload,'avgcost':rslt_avgcost})

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

