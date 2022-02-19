import numpy as np
import sys

sys.path.append('./')

from robot_model.model import *

class PID():
    def __init__(self):
        # Robots' parameters
        self._model_matrix = get_model_matrix()

        # Controller's parameters
        self._kp_v = 40
        self._kp_w = 80
        self._distance_margin = 0.5 # cm

    def compute_control_actions(self, p, r):
        dx = r[0, :] - p[0, :]
        dy = r[1, :] - p[1, :]
        distances = np.sqrt(np.square(dx) +  np.square(dy))
        angles = self.demap_angles(np.arctan2(dy, dx))
        mask = (distances >= self._distance_margin).astype(float)
        vs = self._kp_v*distances * mask
        ws = self._kp_w*self.map_angles(angles - p[2, :]) * mask
        wheel_speeds = self.compute_wheel_speeds(vs, ws)
        return wheel_speeds

    def compute_wheel_speeds(self, v, w):
        inputs = np.vstack((v, w))
        speeds = np.dot(self._model_matrix, inputs)
        return speeds

    def map_angles(self, angles):
        # Maps from (0, 2pi) ---> (-pi, pi)
        return ((angles + np.pi) % (2*np.pi)) - np.pi

    def demap_angles(self, angles):
        # Maps from (-pi, pi) ---> (0, 2pi)
        return (2*np.pi + angles) * (angles < 0) + angles * (angles >= 0)
