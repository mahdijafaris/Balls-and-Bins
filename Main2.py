# This file simulates the randomly selection of the server using power of two choices
# This file simulates the randomly selection of the server
# but there is no power of two choices
from __future__ import division
import math
import matplotlib.pyplot as plt
#import networkx as nx
from multiprocessing import Pool
import numpy as np
import time
#import string
#from BallsBins import *
#from BallsBins.Server import Server
from BallsBins.Simulator2 import Simulator2

#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt

# Pool size for parallel processing
pool_size = 2

# Simulation parameters
srv_num = 1000 # number of servers
cache_sz = 2 # Cache size of each server (expressed in number of files)
file_num = 20 # Number of files


if __name__ == '__main__':
    # Create a number of workers for parallel processing
    pool = Pool(processes=pool_size)

    t_start = time.time()

    i = -1
    result = np.zeros((len(range(1,file_num,3)),3))
    for cache_sz in range(1,file_num,3):
        i = i + 1
        tmpmxld = 0
        tmpavgcst = 0
        params = [(srv_num, cache_sz, file_num) for itr in range(5)]
        print(params)
#        results = pool.map(Simulator1, params)
        results = map(Simulator1, params)
#            rslt = pool.apply_async(Simulator1,(srv_num, cache_sz, file_num,))
#            tmpmxld = tmpmxld + rslt.get()['maxload']
#            tmpavgcst = tmpavgcst + rslt.get()['avgcost']
        for rslt in results:
            tmpmxld = tmpmxld + rslt['maxload']
            tmpavgcst = tmpavgcst + rslt['avgcost']
        result[i,0] = cache_sz
        result[i,1] = tmpmxld/5
        result[i,2] = tmpavgcst/5

    t_end = time.time()
    print("The runtime is {}".format(t_end-t_start))

    plt.plot(result[:,0], result[:,1])
    plt.plot(result[:,0], result[:,2])
    plt.xlabel('Cache size in each server (# of files)')
    plt.show()

    #print(result['loads'])
    #print("------")
    #print('The maximum load is {}'.format(result['maxload']))
    #print('The average request cost is {0:0}'.format(result['avgcost']))

    #fl_lst = [srvs[i].get_files_list() for i in range(n)]
    #print(fl_lst)

    # Draw the graph
    #nx.draw(G)
    #plt.show()






import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
#import string
#from BallsBins import *
from BallsBins.Server import Server

#--------------------------------------------------------------------
log = math.log
sqrt = math.sqrt

# Simulation parameters
n = 120 # number of servers
M = 20 # Cache size of each server (expressed in number of files)
file_num = 20 # Number of files
RGG_radius = sqrt(5/4*log(n))/sqrt(n)

#
file_index = range(file_num) # index of files; from 0 to file_num
file_sets = [[] for i in range(file_num)] # list of sets of servers containing each file

#print(file_sets)

# Generate a random geometric graph.
print('Start generating a random graph with {} nodes...'.format(n))
conctd = False
while not conctd:
    G = nx.random_geometric_graph(n, RGG_radius)
    conctd = nx.is_connected(G)

print('Succesfully generates a connected graph...')
# Draw the graph
#nx.draw(G)
#plt.show()

# Create n servers from the class server
srvs = [Server(i) for i in range(n)]

# Randomly places M files in each servers
for i in range(n):
#    print(i)
    list = np.random.permutation(file_num)[0:M]
    srvs[i].set_files_list(list)
    for j in range(len(list)):
        if i not in file_sets[list[j]]:
            file_sets[list[j]].append(i)


# Main loop of the simulator. We throw n balls requests into the servers.
# Each request randomly pick a server and a file.
for i in range(n):
#    print(i)
    incoming_srv = np.random.randint(n) # Random incoming server
    rqstd_file = np.random.randint(file_num) # Random requested file
    if incoming_srv in file_sets[rqstd_file]:
        srv0 = incoming_srv
    else:
        srv0 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]

    srv1 = srv0
    if len(file_sets[rqstd_file]) > 1:
        while srv1 == srv0:
            srv1 = file_sets[rqstd_file][np.random.randint(len(file_sets[rqstd_file])+1) - 1]

#    print(srv0,' ', srv1)

    load0 = srvs[srv0].get_load()
    load1 = srvs[srv1].get_load()

# Implement power of two choices
#    if load0 > load1:
#        srvs[srv1].add_load()
#    elif load0 < load1:
#        srvs[srv0].add_load()
#    elif np.random.randint(2) == 0:
#        srvs[srv0].add_load()
#    else:
#        srvs[srv1].add_load()

# Implement random placement without considering loads
    srvs[srv0].add_load()

# At the end of simulation, find maximum load, etc.
loads = [srvs[i].get_load() for i in range(n)]
maxload = max(loads)


print(loads)
print("------")
print(maxload)

#fl_lst = [srvs[i].get_files_list() for i in range(n)]
#print(fl_lst)

# Draw the graph
#nx.draw(G)
#plt.show()