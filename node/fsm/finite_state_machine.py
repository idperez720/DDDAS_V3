import numpy as np
import multiprocessing as mp
import time, sys

sys.path.append('./')  # To import modules from upper folder

from pid_control.pid import PID
from population_dynamics.dt_dynamics import *

def run_navigation_controller(communicator):
    global target_pos_array
    target_pos = np.zeros((2, 1))
    controller = PID()
    stop_flag = False
    while(not stop_flag):
        pose, stop_flag = communicator.get_robot_pose()
        target_pos[0, 0] = target_pos_array[0]
        target_pos[1, 0] = target_pos_array[1]
        wheel_speeds = controller.compute_control_actions(pose, target_pos)
        communicator.send_motors_commands(wheel_speeds)
        time.sleep(0.1)

def compute_fitness_functions(population_portions, displacements):
    return (displacements - population_portions).reshape(-1, 1)

def run_state(communicator):
    # Receives the displacements from the station
    msg, complete_message = communicator.get_message_from_station()
    if(not complete_message or not len(msg) == 4):
        print('ERROR: received an incomplete message (run_state 1).')
        return
    else:
        displacements = np.array(list(map(float, msg[:-2]))).reshape(2)

    # Receives the initial robot pose from the camera server
    pose, stop_flag = communicator.get_robot_pose()
    if(stop_flag):
        print('ERROR: received an incomplete message (run_state 2).')
        return
    else:
        global target_pos_array
        target_pos_array = mp.Array('d', 2)
        target_pos_array[0] = pose[0]
        target_pos_array[1] = pose[1]

    # Launches navigation controller in a separate process
    navigation_controller = mp.Process(target=run_navigation_controller, args=[communicator])
    navigation_controller.start()

    # Launches main process
    stop_flag = False
    while(not stop_flag):
        population_portions = np.array([target_pos_array[0], target_pos_array[1]])
        fitnesses = compute_fitness_functions(population_portions, displacements)
        message = np.hstack((fitnesses.reshape(-1), population_portions))
        communicator.send_message_to_station(message)

        msg, complete_message = communicator.get_message_from_station()
        stop_flag = (not complete_message) or (msg[0] == 'exit')

        if(not stop_flag):
            neighbors_info = np.array(list(map(float, msg[:-2]))).reshape(4, -1)
            new_population_portions = DT_DPDs(population_portions, fitnesses, neighbors_info)
            target_pos_array[0] = new_population_portions[0]
            target_pos_array[1] = new_population_portions[1]

    navigation_controller.join()
