import numpy as np

def complete(n):
    graph = np.ones((n, n)) - np.eye(n)
    return graph

def empty(n):
    graph = np.zeros((n, n))
    return graph

def regular_ring_lattice(n, k=2):
    if(n <= 2):
        graph = complete(n)
    else:
        k = np.clip(k, 2, np.round(n/2)*2 - 2) # Bound degree
        k = int(np.round(k/2)*2)               # Make degree even
        graph = np.arange(n) - np.arange(n).reshape(-1, 1)
        graph = ((abs(graph) % (n - k/2)) <= k/2).astype(float)
        graph = np.maximum(graph - np.eye(n), 0) # Remove self loops
    return graph

def cycle(n):
    graph = regular_ring_lattice(n, 2)
    return graph

def path(n):
    diag = np.ones(n-1)
    graph = np.diag(diag, 1) + np.diag(diag, -1)
    return graph

def erdos_renyi(n, p=0.25, connected=True):
    graph = (np.random.random((n, n)) <= p).astype(float)
    if(connected):
        graph = graph + path(n)
    graph = np.clip(graph - np.eye(n), 0, 1) # No self loops, max weight 1
    graph = np.minimum(graph + graph.T, 1) # Keep it undirected
    return graph

def watts_strogatz(n, k=2, p=0.25):
    k = np.clip(k, 2, np.round(n/2)*2 - 2) # Bound degree
    k = int(np.round(k/2)*2)               # Make degree even
    graph = regular_ring_lattice(n, k)
    temp = np.zeros((n, n))
    for i in range(int(k/2)): # TODO: vectorize this (?)
        temp = temp + np.diag(np.ones(n - (i+1)), i+1)
        temp = temp + np.diag(np.ones(i+1), (i+1) - n)
    temp = temp * ((np.random.random((n, n)) <= p).astype(float))
    graph = graph - temp
    ids = np.where((graph + np.eye(n)) == 0)
    for i in range(n): # TODO: vectorize this (?)
        x_ids = np.where(ids[0] == i)
        y_ids = ids[1][x_ids]
        selected = temp[i, y_ids]
        if(np.max(selected) > 0):
            np.random.shuffle(selected)
            temp[i, y_ids] = selected
    graph = graph + temp
    graph = np.minimum(graph + graph.T, 1) # Keep it undirected
    return graph

def barabasi_albert(n, n0=2, p=0.25, connected=True):
    n0 = np.clip(n0, 0, n)
    graph = np.zeros((n, n))
    graph[:n0, :n0] = erdos_renyi(n0, p=p, connected=True)
    for i in range(n0, n):
        for j in range(i):
            d_sum = np.sum(graph)
            link = 1.0*np.random.binomial(1, np.sum(graph[j, :])/d_sum)
            graph[i, j] = link
            graph[j, i] = link
    order = np.arange(n)
    np.random.shuffle(order)
    graph = graph[order, :]
    graph = graph[:, order]
    if(connected):
        graph = graph + path(n)
    graph = np.minimum(graph, 1)
    return graph
