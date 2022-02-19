import numpy as np

# All formations are defined over time.
# The (0, 0) coordinate is in the lower-left corner! As in the R^2 plane.

#==============================CORE FUNCTION====================================

def formatter(n, T, dx, dy, leader_xy, deltas):
    refs = np.zeros((T, 3, n))
    refs[:, :len(leader_xy), 0] = leader_xy
    refs[:, 0, 1:] = dx*deltas[0, :]
    refs[:, 1, 1:] = dy*deltas[1, :]
    return refs[:, :, 0], refs[:, :, 1:], refs

#===============================GIAP FORMATION==================================
# These formations are defined for 6 robots only.

def get_G_formation(n=6, T=500, dx=20, dy=20, leader_xy=[70, 50]):
    deltas = np.array([[1, 1, -1, -1, 1],
                       [0, -1, -1, 1, 2]])
    return formatter(6, T, dx, dy, leader_xy, deltas)

def get_I_formation(n=6, T=500, dx=20, dy=20, leader_xy=[50, 50]):
    deltas = np.array([[0, 0, 0, 0, 0],
                       [1, -1, -2, 2, 3]])
    return formatter(6, T, dx, dy, leader_xy, deltas)

def get_A_formation(n=6, T=500, dx=20, dy=20, leader_xy=[70, 80]):
    deltas = np.array([[-1, -2, 0, -2, -1],
                       [0, -1, -1, 0, 1]])
    return formatter(6, T, dx, dy, leader_xy, deltas)

def get_P_formation(n=6, T=500, dx=20, dy=20, leader_xy=[90, 70]):
    deltas = np.array([[-1, -2, -2, -2, -1],
                       [-1, -1, -3, 1, 1]])
    return formatter(6, T, dx, dy, leader_xy, deltas)

def get_GIAP_formation(n=6, T=2000, dx=None, dy=None, leader_xy = []):
    l_G, f_G = get_G_formation(T=T//4)
    l_I, f_I = get_I_formation(T=T//4)
    l_A, f_A = get_A_formation(T=T//4)
    l_P, f_P = get_P_formation(T=T//4)
    l_rs = np.concatenate((l_G, l_I, l_A, l_P), axis=0)
    f_rs = np.concatenate((f_G, f_I, f_A, f_P), axis=0)
    return l_rs, f_rs

#=================================STANDARD FORMATIONS===========================

def get_diagonal_formation(n, T=500, dx=10, dy=10, leader_xy=[20, 80]):
    deltas = np.vstack((np.arange(1, n), -np.arange(1, n)))
    return formatter(n, T, dx, dy, leader_xy, deltas)

def get_triangle_formation(n, T=500, dx=10, dy=10, leader_xy=[62.5, 65]):
    print('WARNING: THIS FORMATION IS BOUNDED UP TO SIX (6) ROBOTS!')
    n = np.clip(n, 1, 6)
    nf = np.maximum(n-1, 1)
    deltas = np.array([[1, 2, 0, -2, -1][:nf],
                       [-1, -2, -2, -2, -1][:nf]]).reshape(2, nf)
    return formatter(n, T, dx, dy, leader_xy, deltas)

def get_horizontal_line_formation(n, T=500, dx=10, dy=10, leader_xy=[70, 50]):
    xs = np.arange(1, n)
    xs[int(np.ceil((n-1)/2)):] -= n
    deltas = np.vstack((xs, np.zeros(n-1)))
    return formatter(n, T, dx, dy, leader_xy, deltas)

def get_vertical_line_formation(n, T=500, dx=10, dy=10, leader_xy=[70, 50]):
    ys = np.arange(1, n)
    ys[int(np.ceil((n-1)/2)):] -= n
    deltas = np.vstack((np.zeros(n-1), ys))
    return formatter(n, T, dx, dy, leader_xy, deltas)

def get_hexagonal_formation(n, T=500, dx=10, dy=10, leader_xy=[62.5, 65]):
    print('WARNING: THIS FORMATION IS BOUNDED UP TO SIX (6) ROBOTS!')
    n = np.clip(n, 1, 6)
    nf = np.maximum(n-1, 1)
    deltas = np.array([[2, 2, 0, -2, -2][:nf],
                       [-1, -3, -4, -3, -1][:nf]]).reshape(2, nf)
    return formatter(n, T, dx, dy, leader_xy, deltas)

#================================CUSTOM FORMATIONS==============================
def get_custom_formation_1(n=6, T=2000, dx=None, dy=None, leader_xy = []):
    l_line, f_line = get_horizontal_line_formation(n, T=T//4, leader_xy=[70, 50])
    l_hex, f_hex = get_hexagonal_formation(n, T=T//2, leader_xy=[100, 50])
    l_rs = np.concatenate((l_line, l_hex, l_line), axis=0)
    f_rs = np.concatenate((f_line, f_hex, f_line), axis=0)
    return l_rs, f_rs

def get_custom_formation_2(n=6, T=2000, dx=None, dy=None, leader_xy = []):
    l_hex1, f_hex1 = get_hexagonal_formation(n, T=T//4, leader_xy=[70, 50])
    l_hex2, f_hex2 = get_hexagonal_formation(n, T=T//4, leader_xy=[80, 60])
    l_hex3, f_hex3 = get_hexagonal_formation(n, T=T//4, leader_xy=[90, 50])
    l_hex4, f_hex4 = get_hexagonal_formation(n, T=T//4, leader_xy=[100, 40])
    l_rs = np.concatenate((l_hex1, l_hex2, l_hex3, l_hex4), axis=0)
    f_rs = np.concatenate((f_hex1, f_hex2, f_hex3, f_hex4), axis=0)
    return l_rs, f_rs
