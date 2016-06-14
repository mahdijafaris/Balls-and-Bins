import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import csv


# Choose the simulator. It can be the following values:
# 'one choice'
# 'two choice'
#simulator = 'one choice'
simulator = 'two choice'

srv_num = 400
file_num = 50
# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 36

"""
rslt = []
with open('output.csv','rb') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        print(row)
        rslt.append((map(float, row)))
"""

#result = np.array([])
if simulator == 'one choice':
    #with open('one_choice_sn={}_fn={}_itr={}.mat'.format(srv_num,file_num,num_of_runs),'rb') as f:
    mat_contents = sio.loadmat('CacheSzVar_one_choice_sn={}_fn={}_itr={}.mat'.format(srv_num,file_num,num_of_runs))
elif simulator == 'two choice':
    #with open('two_choice_sn={}_fn={}_itr={}.txt'.format(srv_num,file_num,num_of_runs),'rb') as f:
    mat_contents = sio.loadmat('CacheSzVar_two_choice_sn={}_fn={}_itr={}.mat'.format(srv_num,file_num,num_of_runs))


rslt_maxload = mat_contents['maxload']
rslt_avgcost = mat_contents['avgcost']

print(rslt_maxload)
print(rslt_avgcost)

avg_maxload = np.sum(rslt_maxload[:,1:rslt_maxload.shape[1]],axis=1)/num_of_runs
avg_avgcost = np.sum(rslt_avgcost[:,1:rslt_avgcost.shape[1]],axis=1)/num_of_runs

print(avg_maxload)
print(avg_avgcost)

#line_maxload, = plt.plot(result[:,0], result[:,1], label='Maximum Load')
#line_avgCost, = plt.plot(result[:,0], result[:,2], label='Average Cost')
line_maxload, = plt.plot(rslt_maxload[:,0], avg_maxload, 'b', label='Maximum Load')
plt.plot(rslt_maxload[:,0], avg_maxload, 'ko')
#plt.plot(result[:,0], result[:,1], 'ko')
line_avgCost, = plt.plot(rslt_avgcost[:,0], avg_avgcost, 'r', label='Average Cost')
plt.plot(rslt_avgcost[:,0], avg_avgcost, 'k^')
#plt.plot(result[:,0], result[:,2], 'k^')
#line_maxload.set_label('Label via method')
plt.legend()
plt.xlabel('Cache size in each server (# of files)')
plt.title('Simulator: {}. # of servers = {}, # of files = {}, # of iterations ={}'.format(simulator,srv_num,file_num,num_of_runs))
plt.show()
