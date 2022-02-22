import numpy as np
import sys, time
from communication.node_communicator import Node_Comunicator
#from fsm.finite_state_machine import *
from fsm.finite_state_machine_with_reconfiguration import *

def main_atack():
    # Creates server socket and launches server
    communicator = Node_Comunicator()
    communicator.bind_server_socket()
    communicator.run_server()

    # Waits for command from the station to connect to the camera server
    msg, complete_message = communicator.get_message_from_station()
    if(complete_message and msg[0] == 'cam'):
        communicator.connect_to_camera()
    else:
        sys.exit()
    print('Connected to camera server!')

    # Connects to the assigned robot
    address_set = communicator.set_robot_ip_address()
    if(address_set):
        communicator.connect_to_robot()
    else:
        sys.exit()
    print('Connected to assigned robot!')

    # Lauches main loop (finite state machine)
    stop_flag = False
    while(not stop_flag):
        msg, complete_message = communicator.get_message_from_station()  # Waits command from station

        if(complete_message):
            if(msg[0] == 'exit'):
                print('Closing finite state machine!')
                stop_flag = True

            elif(msg[0] == 'run'):
                run_state(communicator)
                stop_flag = True

        elif(not complete_message):
            print('Received an incomplete message from the station. Closing...')
            stop_flag = True

    communicator.close()
    print('Node closed.')
