import math
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
#import csv


# Choose the simulator. It can be the following values:
# 'one choice'
# 'two choice'
simulator = 'one choice'
#simulator = 'two choice'

#srv_num = 2000
file_num = 2000
cache_cz = 10
# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 80

"""
rslt = []
with open('output.csv','rb') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        print(row)
        rslt.append((map(float, row)))
"""

result = np.array([])
if simulator == 'one choice':
    #with open('rslt2_sim1_fn={}_cs={}_itr={}.txt'.format(file_num,cache_cz,num_of_runs),'rb') as f:
    mat_contents = sio.loadmat('SrvSzVar_one_choice_fn={}_cs={}_itr={}.mat'.format(file_num, cache_cz, num_of_runs))
        #result = np.loadtxt(f, delimiter=',')
elif simulator == 'two choice':
    #with open('rslt2_sim2_fn={}_cs={}_itr={}.txt'.format(file_num,cache_cz,num_of_runs),'rb') as f:
    mat_contents = sio.loadmat('SrvSzVar_two_choice_fn={}_cs={}_itr={}.mat'.format(file_num, cache_cz, num_of_runs))
        #result = np.loadtxt(f, delimiter=',')


rslt_maxload = mat_contents['maxload']
rslt_avgcost = mat_contents['avgcost']

print(rslt_maxload)
print(rslt_avgcost)

avg_maxload = np.sum(rslt_maxload[:,1:rslt_maxload.shape[1]],axis=1)/num_of_runs
avg_avgcost = np.sum(rslt_avgcost[:,1:rslt_avgcost.shape[1]],axis=1)/num_of_runs

print(avg_maxload)
print(avg_avgcost)

#for i in range(result.shape[0]):
#    result[i,0] = math.log(result[i,0])
    #result[i,2] = math.log(result[i,2])

line_maxload, = plt.plot(rslt_maxload[:,0], avg_maxload, 'b', label='Maximum Load')
plt.plot(rslt_maxload[:,0], avg_maxload, 'ko')
line_avgCost, = plt.plot(rslt_avgcost[:,0], avg_avgcost, 'r', label='Average Cost')
plt.plot(rslt_avgcost[:,0], avg_avgcost, 'k^')
#line_maxload.set_label('Label via method')
#plt.xscale('log')
#plt.legend()
plt.legend(loc=4,
           bbox_transform=plt.gcf().transFigure)
plt.xlabel('Number of servers')
plt.title('Simulator: {}. # of files = {}, cache size = {}, # of iterations ={}'.format(simulator,file_num,cache_cz,num_of_runs))
plt.show()
