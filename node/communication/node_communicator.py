import numpy as np
import multiprocessing as mp
import sys, socket, time

sys.path.append('./')
from robot_model.model import *

class Node_Comunicator():
    def __init__(self):
        self._station_ip_address = '192.168.0.199'  # ip address of main station
        self._buffer_size = 256
        self._msg_delimiter = '/'
        self._msg_end = 'z'
        self._msg_tail = self._msg_delimiter + self._msg_end + self._msg_delimiter

        # Variables
        self._ps = np.zeros((3, 1)) # x-y-phi
        self._robot_log = np.zeros((3, 1)) # x-y-phi

        # Multiprocessing variables
        self._robot_log_array = mp.Array('d', 3)    # Multiprocessing array with [xs, ys, phis]

        # Flags
        self._connected_to_camera_server = False

        # Initialization
        self.init_robot_message()

    def bind_server_socket(self):
        # Station socket (as server)
        self._station_sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._station_sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._station_sckt.bind(('', 2000))

    def connect_to_camera(self):
        # Camera socket (as client)
        self._camera_sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._camera_sckt.connect((self._station_ip_address, 3000))
        self._connected_to_camera_server = True

    def connect_to_robot(self):
        # Camera socket (as client)
        self._robot_sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._robot_sckt.connect((self._robot_ip_address, 1000))
        self.set_robot_leds(state = 'on') # To check connection

    def run_server(self):
        print('Server is running!')
        self._station_sckt.listen()
        self._station_conn, self._station_addr = self._station_sckt.accept()
        print('Connected to:', self._station_addr[0])

    def check_message(self, msg):
        if(msg.count(self._msg_end) == 1 and msg[-2] == self._msg_end):
            return True
        else:
            return False

    def get_message_from_station(self):
        msg = self._station_conn.recv(self._buffer_size).decode('utf-8').split(self._msg_delimiter)
        return msg, self.check_message(msg)

    def send_message_to_station(self, message): #msg should be a list or numpy array
        msg = self._msg_delimiter.join(list(map(str, message)))
        self._station_conn.sendall(bytes(msg + self._msg_tail, 'utf-8'))

    def get_robot_pose(self):
        self._camera_sckt.sendall(bytes('pos' + self._msg_tail, 'utf-8'))
        msg = self._camera_sckt.recv(self._buffer_size).decode('utf-8').split(self._msg_delimiter)
        complete_message = self.check_message(msg)
        if(complete_message):
            if(msg[0] == 'exit'):
                stop_flag = True
            else:
                self._ps[:, 0] = list(map(float, msg[:-2]))
                stop_flag = False
        else:
            stop_flag = True
        return self._ps.copy(), stop_flag

    def get_robot_ip_address(self):
        self._camera_sckt.sendall(bytes('addr' + self._msg_tail, 'utf-8'))
        msg = self._camera_sckt.recv(self._buffer_size).decode('utf-8').split(self._msg_delimiter)
        complete_message = self.check_message(msg)
        robot_ip_address = '0'
        if(complete_message):
            if(msg[0] == 'exit'):
                stop_flag = True
            else:
                robot_ip_address = msg[0]
                stop_flag = False
        else:
            stop_flag = True
        return robot_ip_address, stop_flag

    def set_robot_ip_address(self):
        addr, stop_flag = self.get_robot_ip_address()
        if(not stop_flag):
            self._robot_ip_address = addr
            return True
        else:
            print('ERROR: could not set robot IP address!')
            return False

    def set_robot_leds(self, state='on'):
        msg = self._robot_message.copy()
        if state == 'on':
            msg[7] = '07'
        else:
            msg[7] = '00'
        msg = ''.join(msg)
        msg = bytes.fromhex(msg)
        self._robot_sckt.sendall(msg)

    def start_robot_data_server(self): # Do not call this method before the camera connection
        if(self._connected_to_camera_server):
            self._robot_message[1] = '02' # Enables data streaming without robot camera
            robot_log, _ = self.get_robot_pose()
            auxiliar = np.unwrap( [0, robot_log[2]] )
            robot_log[2] = auxiliar[1]
            for i in range(3):
                self._robot_log_array[i] = robot_log[i, 0]
            robot_data_server = mp.Process(target=self.run_robot_data_server)
            robot_data_server.daemon = True
            robot_data_server.start()
        else:
            print('\nERROR: not connected to camera server!')

    def run_robot_data_server(self):
        k = 0
        while(True):
            data = self._robot_sckt.recv(self._buffer_size)
            if(len(data) == 104):
                lsl, msl, lsr, msr = data[79], data[80], data[81], data[82]
                right, left = lsr + msr*256, lsl + msl*256
                if(k == 0):
                    r_count_prev, l_count_prev = right, left
                    k += 1
                r_delta = self.map_stepper_count(right, r_count_prev)
                l_delta = self.map_stepper_count(left, l_count_prev)
                r_count_prev = right
                l_count_prev = left
                delta_x, delta_y, delta_phi = convert_wheel_displacements(r_delta, l_delta, self._robot_log_array[2])
                self._robot_log_array[0] = self._robot_log_array[0] + delta_x
                self._robot_log_array[1] = self._robot_log_array[1] + delta_y
                self._robot_log_array[2] = self._robot_log_array[2] + delta_phi

    def get_robot_data(self):
        for i in range(3):
            self._robot_log[i, 0] = self._robot_log_array[i]
        return self._robot_log.copy()

    def send_motors_commands(self, speeds):
        # speeds must be an array of shape (2, 1)
        msg = self._robot_message.copy()
        msg[4], msg[3] = self.map_speed(speeds[0, 0])
        msg[6], msg[5] = self.map_speed(speeds[1, 0])
        msg = ''.join(msg)
        msg = bytes.fromhex(msg)
        self._robot_sckt.sendall(msg)

    def map_speed(self, value):
        value = np.clip(value, -1000, 1000)
        value = abs(value) if value >= 0 else 65536 + value # 2**16 = 65536 (Two's complement)
        speed = '000' + hex(int(value))[2:]
        speed = speed[::-1]
        speed = speed[:4][::-1]
        return speed[0:2], speed[2:4] # MSB, LSB

    def map_stepper_count(self, count, count_prev):
        delta = count - count_prev
        if(abs(delta) >= 1000):
            alpha = np.maximum(count, count_prev)
            beta = np.minimum(count, count_prev)
            delta = -(65535 - alpha + beta)*np.sign(delta)
        return delta

    def init_robot_message(self):
        id = '80'
        flags_req = '00'
        flags_set = '00'
        motor_left_LSB = '00'
        motor_left_MSB = '00'
        motor_right_LSB = '00'
        motor_right_MSB = '00'
        leds_state = '00'
        leds_rgb = '00'*12
        sound = '00'
        self._robot_message = [id, flags_req, flags_set,
                               motor_left_LSB, motor_left_MSB,
                               motor_right_LSB, motor_right_MSB,
                               leds_state, leds_rgb, sound]

    def close_station_connection(self): # Station
        self._station_conn.close()
        self._station_sckt.close()

    def close_camera_connection(self): # Camera
        self._camera_sckt.close()
        self._connected_to_camera_server = False

    def close_robot_connection(self): # Robot
        self.send_motors_commands(np.zeros((2, 1))) # Turn off all motors
        self.set_robot_leds(state = 'off')
        time.sleep(0.5)
        self._robot_sckt.close()

    def close(self):
        self.close_camera_connection()
        self.close_station_connection()
        self.close_robot_connection()
