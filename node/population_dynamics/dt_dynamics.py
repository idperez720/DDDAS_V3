import numpy as np


def DT_DPDs(population_portions, fitnesses, neighbors_info):
    # population_portions is a (2,) array with the population portions of the current agent
    # fitnesses is a (2, 1) array with the fitnesses of the current agent
    # neighbors_info is an array of shape(4, num_neighbors) that has (fx, fy, px, py) of all the neighboring agents
    # This function should return the new population portions in a (2,) array: (px_new, py_new)
    epsilons = (1 / neighbors_info.shape[1]) * np.ones(2)
    neighbors_fitnesses = neighbors_info[:2, :]
    fitness_differences = fitnesses - neighbors_fitnesses
    return population_portions + epsilons * np.sum(fitness_differences, 1)

def DT_DRDs(population_portions, fitnesses, neighbors_info):
    # population_portions is a (2,) array with the population portions of the current agent
    # fitnesses is a (2, 1) array with the fitnesses of the current agent
    # neighbors_info is an array of shape(4, num_neighbors) that has (fx, fy, px, py) of all the neighboring agents
    # This function should return the new population portions in a (2,) array: (px_new, py_new)
    epsilons = 0.01 * np.ones(2)
    neighbors_fitnesses = neighbors_info[:2, :]
    neighbors_portions = neighbors_info[2:, :]
    fitness_differences = fitnesses - neighbors_fitnesses
    return population_portions + epsilons * population_portions * np.sum(neighbors_portions * fitness_differences, 1)

def DT_DSDs(population_portions, fitnesses, neighbors_info):
    # population_portions is a (2,) array with the population portions of the current agent
    # fitnesses is a (2, 1) array with the fitnesses of the current agent
    # neighbors_info is an array of shape(4, num_neighbors) that has (fx, fy, px, py) of all the neighboring agents
    # This function should return the new population portions in a (2,) array: (px_new, py_new)
    num_neighbors = neighbors_info.shape[1]
    epsilons = 0.01 * np.ones(2)
    neighbors_fitnesses = neighbors_info[:2, :]
    neighbors_portions = neighbors_info[2:, :]
    fitness_differences = fitnesses - neighbors_fitnesses
    own_portions_matrix = population_portions.reshape(2,1) * np.ones((2, num_neighbors))
    signs = np.sign(fitness_differences)
    portions = (neighbors_portions * np.maximum(signs, 0)) - (own_portions_matrix * np.minimum(signs, 0))
    return population_portions + epsilons * population_portions * np.sum(portions * fitness_differences, 1)
