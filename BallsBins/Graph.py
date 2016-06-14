import networkx as nx
import math
import sys
#import matplotlib.pyplot as plt

sqrt = math.sqrt


# This function return a square lattice graph.
# The lattice size should be a perfect square.
def Gen2DLattice(size):
    side = sqrt(size)
    if not side.is_integer():
        print("Error: the size of lattice is not perfect square!")
        sys.exit()

    G = nx.empty_graph(size)

    for i in range(size):
        r = i // side
        c = i % side
        # Now we have to add 4 edges to the neighbours of i_th node
        # Adding edge to the neighbour: (r+1,c)
        l = ((r+1) % side) * side + c
        G.add_edge(i,l)
        # Adding edge to the neighbour: (r-1,c)
        l = ((r-1) % side) * side + c
        G.add_edge(i,l)
        # Adding edge to the neighbour: (r,c+1)
        l = r * side + ((c+1) % side)
        G.add_edge(i,l)
        # Adding edge to the neighbour: (r,c-1)
        l = r * side + ((c-1) % side)
        G.add_edge(i,l)

    return G
