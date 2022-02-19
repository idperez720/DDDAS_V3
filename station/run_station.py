import numpy as np
import multiprocessing as mp
import socket, time
from communication.camera_server import Camera_Server
from detection.detector import Detector
from graphs.models import *
from formations.formations import *

class Main_Station(Camera_Server, Detector):
    def __init__(self, robots=['blue', 'purple', 'red', 'green', 'lime', 'yellow']):
        Camera_Server.__init__(self, robots=robots)
        Detector.__init__(self, robots=robots)

        # Core variables
        self._dt = 0.1

        # Station variables
        self._system_info = np.zeros((4, self._n + 1)) # fx, fy, px, py
        self._graph = path(self._n + 1)
        leader_target, follower_displacements, _ = get_hexagonal_formation(self._n + 1, T=1)
        self._leader_target = leader_target[0, :-1]
        self._follower_displacements = follower_displacements[0, :-1, :]

        # Create sockets
        self._station_sckts = []
        for addr in self._node_addresses:
            sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sckt.connect((addr, 2000))
            self._station_sckts.append(sckt)

        # Multiprocessing variables
        self._positions_array = mp.Array('d', self._n*3)    # Multiprocessing array with [xs, ys, phis]
        self._targets_array = mp.Array('d', self._n*3)      # Multiprocessing array with [xs, ys, phis]
        self._keep_running = mp.Array('i', [1])             # Controller running flag

        # Run processes
        self.execute_multiprocesses()

    def execute_multiprocesses(self):
        camera_server = mp.Process(target = self.run_camera_server)
        camera_server.daemon = True
        detector = mp.Process(target = self.run_camera, args=[True, False])

        camera_server.start()
        detector.start()

        time.sleep(1)
        self.send_message_to_all_nodes('cam')
        time.sleep(1)

        self.send_message_to_all_nodes('run')

        self.run_station()

        detector.join() # Waits for the cammera process to finish

        self.close_camera_server()
        self.close_detector()

        self.send_message_to_all_nodes('exit')

    def run_station(self):
        # Initialization
        for i, sckt in enumerate(self._station_sckts):
            msg = self._msg_delimiter.join(list(map(str, self._follower_displacements[:, i])))
            sckt.sendall(bytes(msg + self._msg_tail, 'utf-8'))
        # Main loop
        while(self._keep_running[0] == 1):
            self.update_system_info()
            self.update_mp_targets()
            time.sleep(self._dt)
            for i, sckt in enumerate(self._station_sckts):
                neighbors_info = self._system_info[:, np.where(self._graph[i+1, :] == 1)].reshape(-1)
                msg = self._msg_delimiter.join(list(map(str, neighbors_info)))
                sckt.sendall(bytes(msg + self._msg_tail, 'utf-8'))

    def update_system_info(self):
        self._system_info[:2, 0] = -self._leader_target.reshape(2)
        for i, sckt in enumerate(self._station_sckts):
            msg = sckt.recv(self._buffer_size).decode('utf-8').split(self._msg_delimiter)
            if(msg.count(self._msg_end) == 1 and msg[-2] == self._msg_end):
                self._system_info[:, i+1] = list(map(float, msg[:-2]))
            else:
                print('ERROR: an incomplete message was received from:', self._node_addresses[i])
                self._keep_running[0] = 0
        # TODO: UPDATE POPULATION STATE OF THE LEADER (or run the leader in a separate node)

    def update_mp_targets(self):
        for i in range(self._n):
            self._targets_array[i] = self._system_info[2, i+1]
            self._targets_array[i + self._n] = self._system_info[3, i+1]

    def send_message_to_all_nodes(self, msg):
        for sckt in self._station_sckts:
            sckt.sendall(bytes(msg + self._msg_tail, 'utf-8'))

    def close_sockets(self):
        for sckt in self._station_sckts:
            sckt.close()
        print('Closed all sockets!')

if __name__ == '__main__':
    station = Main_Station(robots=['purple'])#, 'red', 'yellow'])
