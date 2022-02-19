import numpy as np
import multiprocessing as mp
import time, sys

sys.path.append('./')  # To import modules from upper folder

from pid_control.pid import PID
from reconfiguration.sensor_reconfigurator import Sensor_Reconfigurator

def run_navigation_controller(communicator):
    global target_pos_array
    target_pos = np.zeros((2, 1))
    p2 = communicator.get_robot_data()
    p1 = p2.copy()
    p1Attacked = p1.copy()
    p2Attacked = p2.copy()

    controller = PID()
    Auxiliar = p1Attacked.copy()
    Auxiliar = np.unwrap([0, Auxiliar[2]])
    Auxiliar = Auxiliar[1]
    p1Attacked[2] = Auxiliar.copy()
    reconfigurator = Sensor_Reconfigurator(p1Attacked, p2Attacked, controller)
    stop_flag = False

    intial_time = time.time()
    while(not stop_flag):
        p1, stop_flag = communicator.get_robot_pose()
        p2 = communicator.get_robot_data()
        p1Attacked = p1.copy()

        Auxiliar2 = p1Attacked.copy()
        Auxiliar = np.unwrap([Auxiliar, Auxiliar2[2]])
        Auxiliar = Auxiliar[1]
        p1Attacked[2] = Auxiliar.copy()

        p2Attacked = p2.copy()

        if time.time()-intial_time>5:
            p2Attacked[0] = p2Attacked[0] + 40
            print('Attack on sensor 2!')
            print(p2Attacked)
        target_pos[0, 0] = target_pos_array[0]
        target_pos[1, 0] = target_pos_array[1]
        pose_estimation = reconfigurator.compute_convex_combination(p1Attacked.copy(), p2Attacked.copy(), target_pos)

        wheel_speeds = controller.compute_control_actions(pose_estimation, target_pos)
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
        target_pos_array[0] = pose[0, 0]
        target_pos_array[1] = pose[1, 0]

    # Launches navigation controller in a separate process
    communicator.start_robot_data_server()
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
            neighbors = np.array(list(map(float, msg[:-2]))).reshape(2, -1)
            new_population_portions = population_portions + (1/neighbors.shape[1]) * np.sum(fitnesses - neighbors, 1)
            target_pos_array[0] = new_population_portions[0]
            target_pos_array[1] = new_population_portions[1]

    navigation_controller.join()
