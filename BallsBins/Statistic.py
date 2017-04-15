# This module implement some statistical functions and classes

import numpy as np
import scipy.stats as stats


# This function return a random variable X \in {1,...,n}
# with Zipf distribution

def bounded_zipf(n, gamma, smpl_nmbr):
    gamma = float(gamma)
    x = np.arange(1, n)
    weights = x ** (-gamma)
    weights /= weights.sum()
    #print weights
    bndd_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))

    sample = bndd_zipf.rvs(size=smpl_nmbr)
    return sample
