import matplotlib.pyplot as plt
import numpy as np
import csv


# Choose the simulator. It can be the following values:
# 'one choice'
# 'two choice'
simulator = 'one choice'
#simulator = 'two choice'

srv_num = 2000
file_num = 2000
# Number of runs for computing average values. It is more eficcient that num_of_runs be a multiple of pool_size
num_of_runs = 120

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
    with open('rslt_sim1_sn={}_fn={}_itr={}.txt'.format(srv_num,file_num,num_of_runs),'rb') as f:
        result = np.loadtxt(f, delimiter=',')
elif simulator == 'two choice':
    with open('rslt_sim2_sn={}_fn={}_itr={}.txt'.format(srv_num,file_num,num_of_runs),'rb') as f:
        result = np.loadtxt(f, delimiter=',')


print(result)
#print(rslt)

#result = np.array(rslt)

line_maxload, = plt.plot(result[:,0], result[:,1], label='Maximum Load')
line_avgCost, = plt.plot(result[:,0], result[:,2], label='Average Cost')
#line_maxload.set_label('Label via method')
plt.legend()
plt.xlabel('Cache size in each server (# of files)')
plt.title('Simulator: {}. # of servers = {}, # of files = {}, # of iterations ={}'.format(simulator,srv_num,file_num,num_of_runs))
plt.show()
