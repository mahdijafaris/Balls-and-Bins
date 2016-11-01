# This file simulates the randomly selection of the server
# but there is no power of two choices
from __future__ import division
import math
#import matplotlib.pyplot as plt
#import networkx as nx
from multiprocessing import Pool
import numpy as np
import time
#import simplejson as json
import csv
#import string
#from BallsBins import *
#from BallsBins.Server import Server
from BallsBins.Simulator1 import Simulator1

#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt

#--------------------------------------------------------------------
# Simulation parameters

# Choose the simulator. It can be the following values:
# 'one choice'
# 'two choice'
simulator = 'one choice'

# Base part of the output file name
base_out_filename = 'output'

# Pool size for parallel processing
pool_size = 4

# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 10

# Simulation parameters
srv_num = 50 # number of servers
#cache_sz = 2 # Cache size of each server (expressed in number of files)
file_num = 20 # Number of files
#--------------------------------------------------------------------


if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    if simulator == 'one choice':
        t_start = time.time()

        i = -1
        result = np.zeros((len(range(1,file_num,3)),3))
        for cache_sz in range(1,file_num,3):
            i = i + 1
            tmpmxld = 0
            tmpavgcst = 0
#            prm1 = []
#            prm2 = []
#            prm3 = []
#            for itr in range(5):
#                rslt = Simulator1(srv_num, cache_sz, file_num)
#                tmpmxld = tmpmxld + rslt['maxload']
#                tmpavgcst = tmpavgcst + rslt['avgcost']
#
#                prm1.append(srv_num)
#                prm2.append(cache_sz)
#                prm3.append(file_num)
#            params = zip(prm1, prm2, prm3)
            params = [(srv_num, cache_sz, file_num) for itr in range(num_of_runs)]
            #print(prm1)
            #print(prm2)
            #print(prm3)
            print(params)
            results = pool.map(Simulator1, params)
#            results = map(Simulator1, params)
#            rslt = pool.apply_async(Simulator1,(srv_num, cache_sz, file_num,))
#            tmpmxld = tmpmxld + rslt.get()['maxload']
#            tmpavgcst = tmpavgcst + rslt.get()['avgcost']
            for rslt in results:
                tmpmxld = tmpmxld + rslt['maxload']
                tmpavgcst = tmpavgcst + rslt['avgcost']
            
            result[i,0] = cache_sz
            result[i,1] = tmpmxld/num_of_runs
            result[i,2] = tmpavgcst/num_of_runs

        t_end = time.time()
        print("The runtime is {}".format(t_end-t_start))

#    print(str(result))
    # write to the file
#    f = open(out_filename, 'w')
#    json.dump(result, f)
    #s = str(result) + '\n'
    #f.write(s)
    #s = str(result[:,1]) + '\n'
    #f.write(s)
    #s = str(result[:,2]) + '\n'
    #f.write(s)
#    f.close()
#    with open('output.csv', 'wb') as csvfile:
#        csv.writer(csvfile).writerows(result.tolist())
#    with open('output.txt', 'wb') as f:
#        result.tofile(f)
#        f.close()
    np.savetxt(base_out_filename+'_sn={}_fn={}.txt'.format(srv_num,file_num), result, delimiter=',')

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

    # Draw the graph
    #nx.draw(G)
    #plt.show()
