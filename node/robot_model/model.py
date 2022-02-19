import numpy as np

wheel_radius = 4.1/2.0  # cm
wheels_distance = 5.3   # cm

def get_model_matrix():
    model_matrix = np.linalg.inv(wheel_radius * np.array([[0.5, 0.5], [-1/wheels_distance, 1/wheels_distance]])) # Useful pre-computation
    return model_matrix

def convert_wheel_displacements(r_delta, l_delta, phi):
    r_dist, l_dist = -r_delta*2*np.pi*wheel_radius/1000, l_delta*2*np.pi*wheel_radius/1000
    delta_x = 0.5*(r_dist + l_dist)*np.cos(phi + (r_dist - l_dist)/(2*wheels_distance))
    delta_y = 0.5*(r_dist + l_dist)*np.sin(phi + (r_dist - l_dist)/(2*wheels_distance))
    delta_phi = (r_dist - l_dist)/wheels_distance
    a = phi + (r_dist - l_dist)/(2*wheels_distance)
    # print( 'angulo: ', a, phi,   np.sin(a) )
    return delta_x, delta_y, delta_phi
