import numpy as np
import os, socket, time, pickle, copy
from _thread import start_new_thread

class Camera_Server():
    def __init__(self, robots=['blue', 'purple', 'red', 'green', 'lime', 'yellow']):

        # Core variables
        self._n = len(robots)
        self._clients = []

        # Load addresses
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'ip_addresses/addresses.pickle')
        with open(path, 'rb') as handle:
            self._robots_addresses = pickle.load(handle)
        self._keys_camera_server = robots

        # RPI addresses
        self._node_addresses = []
        for key in self._keys_camera_server:
            self._node_addresses.append(self._robots_addresses[key][-1])

        # Params
        self._buffer_size = 256
        self._msg_delimiter = '/'
        self._msg_end = 'z'
        self._msg_tail = self._msg_delimiter + self._msg_end + self._msg_delimiter

        # Multiprocessing shared data
        self._positions_array = [0]*(self._n*3) # x-y-phi
        self._keep_running = [1]

        # Server variables
        self._camera_sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._camera_sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._camera_sckt.bind(('', 3000))

    def run_camera_server(self):
        self._camera_sckt.listen()
        client_count = 0
        while(self._keep_running[0] == 1):
            try:
                conn, addr = self._camera_sckt.accept()
                print('Connected to ', addr[0], 'Client #:', client_count)
                start_new_thread(self.manage_client, (conn, addr[0]))
                client_count += 1

            except KeyboardInterrupt:
                self._keep_running[0] = 0

    def manage_client(self, conn, addr):
        id = self._node_addresses.index(addr)
        while(self._keep_running[0] == 1):
            data = conn.recv(self._buffer_size)
            if data:
                msg = data.decode('utf-8').split(self._msg_delimiter)
                if(msg.count(self._msg_end) == 1 and msg[-2] == self._msg_end):
                    if(msg[0] == 'pos'):
                        pose = [self._positions_array[id], self._positions_array[id + self._n], self._positions_array[id + int(2*self._n)]]
                        str_pose = self._msg_delimiter.join(list(map(str, pose))) + self._msg_tail
                        conn.sendall(bytes(str_pose, 'utf-8'))
                    elif(msg[0] == 'addr'):
                        addr = self._robots_addresses[self._keys_camera_server[id]][1]
                        conn.sendall(bytes(addr + self._msg_tail, 'utf-8'))
                else:
                    conn.sendall(bytes('exit' + self._msg_tail, 'utf-8'))
                    self._keep_running[0] = 0
                    print('Received an incomplete or mixed message (EXIT).')
        conn.sendall(bytes('exit' + self._msg_tail, 'utf-8')) # To kill connections
        conn.close()

    def close_camera_server(self):
        self._camera_sckt.close()
        print('\nCamera server is closed!')
