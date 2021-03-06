import sys
import numpy as np
from detection.calibrate_colors import main_calibrate_colors
from communication.blink_to_identify import main_blink_to_identify
from graphs.models import *
from formations.formations import *
from run_station import Main_Station

sys.path.append("./")


def save_model(matrix, model, colors):
    file = {}
    file['Matrix'] = matrix
    file['Model'] = model
    file['Colors'] = colors

    with open('model.pickle', 'wb') as handle:
        pickle.dump(file, handle, protocol=pickle.HIGHEST_PROTOCOL)


def input_colors(N):
    print("Please, enter the name of the color that identify each robot you are working with")
    colors = np.array(["Try"])
    inserting = True
    i = 0
    while inserting:
        color = input("Input a new color: ")
        if color not in colors:
            colors = np.append(colors, color)
            i += 1
        else:
            print("Color already added!")

        if i == N:
            break
    return colors[1:]


def first_choice_option(first_choice):
    global inserting_colors
    global colors
    global N_max
    global N
    N_max = 6
    N = 6

    if first_choice == "1":
        print("""-----------------------------------------------------------------------------------------------\n 
                  The system consists in 4 main devices: The camera, the main station, the raspberries and the E-puck.
                  Each is essential for the correct development of different simulation strategies. In general, 
                  communication protocols are based on the main station, this is the computer were you are running this
                  code. The camera connects the main station through a server that allows the main station to calculate
                  the position of the robots that are set in the platform you are using. In general it is required that
                  such platform has: \n 
                  1. Defined area limits \n
                  2. Constant illumination thoughtout its surfce \n 
                  3. Different color from the ones used to identify the robots \n 
                  In general it is further recommended to notice different colors next to the platforms from other objects such as tapes placed omn the floor,
                  or different objects. These objects must be covered, otherwise the system will not work appropiately
                  Regarding the other devices, the purpose of this platform is to allow the simulation and physical 
                  implementation of descentrilized systems which means the user can define how communication interaction actually
                  happen. This means Raspberrys are the ones that compute their own dynamics and though client-server 
                  scheme obtain information about their position and the ones they can communicate with through the main 
                  station. Finally, raspberries control the robors. \n \n For further info go to the read me file. """)
        input("Press [ENTER] to continue...")
        main()
    elif first_choice == "2":
        print("""----------------------------------------------------------------------------------------------\n
                 Camara filters calibration requires platform requirements discussed on on General idea of the system. 
                 As HSV color space is used,so any missing requirement may led the system to fail, so be aware of this possibility
                 before continuing... """)
        input("Press [ENTER] to continue...")

        while inserting_colors:

            N = int(input("Input the number of robots to identify: "))
            N_max = int(input("Input the total number of robots you are currently working with: "))
            if N_max < N:
                print("Total number of robots can not be greater than the number of robots to identify!!")
                pass

            colors = input_colors(N)
            break

        inserting_colors = False
        print(""" Initializing... \n Select a region of the camera image in the color that identifies each robot""")

        main_calibrate_colors("calibrate", colors, N)

        print("Returning to main section...")
        input("Press [ENTER] to continue...")

    elif first_choice == "3":
        print("""____________________________________________________________________________________\n 
                 In order to set IP addresses and associate each Raspberry with an E-puck robot first you have to 
                 connect them all to the same wifi network and be aware of their respective IP address. This might 
                 seem challenging at first, but raspberries can implement a protocol called SSH so that you can run 
                 code and have general access to its system remotely from another computer. It is further recommended
                 you run each raspberry on a different console to ease the whole process of simulation and physical
                 implementation. If you are using a computer with some linux distribution some commands such as nmap 
                 might be particularly useful as well as using each raspberry's localhost name. On the other hand, if
                  you have doubts on how to connect E-puck robots to a wifi network you might find this guide useful:
                   https://www.gctronic.com/doc/index.php/e-puck2. Once this is done and you have clear each IP 
                   address you might continue...""")
        input("Press [ENTER] to continue...")

        while inserting_colors:

            N = int(input("Input the number of robots to identify: "))
            N_max = int(input("Input the total number of robots you are currently working with: "))
            if N_max < N:
                print("Total number of robots can not be greater than the number of robots to identify!!")
                pass
            colors = input_colors(N)
            break
        inserting_colors = False
        main_blink_to_identify(colors, N, N_max)
        input("Press [ENTER] to continue...")
    elif first_choice == "4":

        print("\n Starting color selection...")
        while inserting_colors:

            N = int(input("Input the number of robots to identify: "))
            N_max = int(input("Input the total number of robots you are currently working with: "))
            if N_max < N:
                print("Total number of robots can not be greater than the number of robots to identify!!")
                pass
            colors = input_colors(N)

    else:
        start_sim()


def construct_personalized_matrix():
    global N_max
    matrix = np.zeros((N_max, N_max))

    building = True
    while building:
        params = input("Please enter the three parameters: ")
        params = params.split(",")
        cond1 = (params[0] not in ["1", "0"])
        cond2 = (int(params[1]) <= 0) or (int(params[2]) <= 0)
        cond3 = (int(params[2]) > int(N_max)) or (int(params[1]) > int(N_max))
        if cond1 or cond2 or cond3:
            print("\n There has been an error!!! Please try again")
        else:
            matrix[int(params[1] - 1), int(params[2]) - 1] = int(params[0])
            print("\n Value has been changed succesfully, do you want to inster another value?")
            more = input("y/n: ")
            if more == "y":
                pass
            else:
                print("\n The defined association matrix defined was : \n ", matrix)
                print("\n Is it correct? ")
                confirmation = input("y/n")
                if confirmation == "y":
                    building = False
                else:
                    print("Returning to inserting values mode...")
    return matrix


def obtain_predefined_model(formation_selec, matrix_selec, mode):
    global N_max
    leader_target, follower_displacements, _ = None, None, None
    Matrix = None
    if formation_selec == "G formation":
        leader_target, follower_displacements, _ = get_G_formation(N_max, T=1)
    elif formation_selec == "I formation":
        leader_target, follower_displacements, _ = get_I_formation(N_max, T=1)
    elif formation_selec == "A formation":
        leader_target, follower_displacements, _ = get_A_formation(N_max, T=1)
    elif formation_selec == "P formation":
        leader_target, follower_displacements, _ = get_P_formation(N_max, T=1)
    elif formation_selec == "GIAP formation":
        leader_target, follower_displacements, _ = get_GIAP_formation(N_max, T=1)
    elif formation_selec == "Diagonal formation":
        leader_target, follower_displacements, _ = get_diagonal_formation(N_max, T=1)
    elif formation_selec == "Triangle formation":
        leader_target, follower_displacements, _ = get_triangle_formation(N_max, T=1)
    elif formation_selec == "Horizontal line formation":
        leader_target, follower_displacements, _ = get_horizontal_line_formation(N_max, T=1)
    elif formation_selec == "Vertical line formation":
        leader_target, follower_displacements, _ = get_vertical_line_formation(N_max, T=1)
    elif formation_selec == "Hexagonal formation":
        leader_target, follower_displacements, _ = get_hexagonal_formation(N_max, T=1)

    num = int(N_max)

    if matrix_selec == "complete":
        Matrix = complete(num)
    elif matrix_selec == "empty":
        Matrix = empty(num)
    elif matrix_selec == "Regular ring lattice":
        Matrix = regular_ring_lattice(num)
    elif matrix_selec == "cycle":
        Matrix = cycle(num)
    elif matrix_selec == "path":
        Matrix = path(num)
    elif matrix_selec == "erdos renyi":
        Matrix = erdos_renyi(num)
    elif matrix_selec == "watts strogatz":
        Matrix = watts_strogatz(num)
    elif matrix_selec == "barabasi albert":
        Matrix = barabasi_albert(num)

    if mode == 1:
        return leader_target, follower_displacements, _
    else:
        return Matrix


def generate_model():
    global N_max
    n = N_max

    print("""\n In orden to generate a personalized formation it is needed to initialize different parameters such as: \n
              1. T: Total number of position calculations \n
              2. dx: x-differential displacement value \n
              3. dy: y-differential displacement value \n
              4. leadex_xy: Reference coordinates value for leader  \n
              5. deltas:  X and Y distances from the leader to the rest of the agents \n
              Hence, once these parameters are initialized a whole new formation can be defined. In general it is advicible
              that dx, dy = 15 and T be a large number, but even if they do not satisfy these conditions the system can 
              still work. """)

    asking_params = True

    print("""By default these parameters value are defined as follows: \n
             T = 500 \n
             dx = 15 \n
             dy = 15 \n
             leadex_xy = [60,60] \n
             This means the only parameter the user has to fulfill is delta variable. This param contains two list with """ +
          str(n - 1) + """ entries, one per each no leader agent. """)

    T = 500
    dx = 15
    dy = 15
    leadex_xy = [60, 60]
    delta = None
    while asking_params:
        print("""\n What parameter do you want to change?\n
              1. T\n
              2. dx \n
              3. dy \n
              4. leadex_xy \n
              5. deltas \n  """)
        selecction = input("Select one parameter or press [ENTER] to continue: ")

        if selecction not in ["1", "2", "3", "4", "5", None]:
            print("Selection incorrect! Please try again...")
        elif selecction == "1":
            try:
                T = int(input("Enter a new value for T. Only int values: "))
            except:
                print("Incorrect input. Please try again")
                pass
        elif selecction == "2":
            try:
                dx = int(input("Enter a new value for dx. Only int values: "))
            except:
                print("Incorrect input. Please try again")
                pass
        elif selecction == "3":
            try:
                dy = int(input("Enter a new value for dy. Only int values: "))
            except:
                print("Incorrect input. Please try again")
                pass
        elif selecction == "4":
            try:
                leadex_xy = input("Enter a new value for leadex_xy as two numbers separated by an SPACE: ").split()
                leadex_xy = np.array(leadex_xy, dtype=float)
                if len(leadex_xy) != 2:
                    print("Incorrect input. Please try again")
                    leadex_xy = [60, 60]
            except:
                print("Incorrect input. Please try again")
                pass
        elif selecction == "5":
            x_dis = input(
                "Enter values of distances on x-axis as a list of " + str(n - 1) + "separated by an SPACE: ").split()
            x_dis = np.array(x_dis, dtype=float)
            y_dis = input(
                "Enter values of distances on y-axis as a list of " + str(n - 1) + "separated by an SPACE: ").split()
            y_dis = np.array(y_dis, dtype=float)

            if len(x_dis) != n - 1 or len(y_dis) != n - 1:
                print("Incorrect input. Please try again")
            else:
                delta = np.zeros((2, n - 1))
                delta[0, :] = y_dis
                delta[1, :] = x_dis
        else:
            if delta != None:
                print("Parameters initialized correctly!")
                asking_params = False
            else:
                print("Delta parameter remain unchaged, please define it first!")
        return formatter(n, T, dx, dy, leader_xy, deltas)


def second_choice_fun(second_selection):
    global N_max
    global colors
    formation_options = ["G formation", "I formation", "A formation", "P formation", "GIAP formation",
                         "Diagonal formation", "Triangle formation", "Horizontal line formation",
                         "Vertical line formation",
                         "Hexagonal formation"]
    adyacence_options = ["complete", "empty", "Regular ring lattice", "cycle", "path", "erdos renyi",
                         "watts strogatz",
                         "barabasi albert"]

    if second_selection == "1":

        print("""\n There are a wide variety of both formations and adyacence matrixes. Firstly, regarding the formations
                 this platform supports: \n
                 1. G formation \n
                 2. I formation \n
                 3. A formation \n
                 4. P formation \n
                 5. GIAP formation \n
                 6. Diagonal formation \n
                 7. Triangle formation \n
                 8. Horizontal line formation \n
                 9. Vertical line formation \n
                 10. Hexagonal formation \n
                 This predifed formations were defined for WORKING ONLY with 6 agents! This means using more or less
                 than this number would lead the system to crush.""")
        formation_num = int(input("Select one of the previous formations: ")) - 1
        selecting = True
        while selecting:
            if formation_num not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                print("Incorrect selection, try again")
                formation = input("Please, select one of the previous formations: ")
            else:
                print("Formation " + formation_options[formation_num] + "was successfully choosed")
                selecting = False
        print("""\n Finally, regarding the different adyacence matrixes available there are: \n 
                    1. Complete \n
                    2. Empty \n
                    3. Regular ring Lattice \n
                    4. Cycle \n
                    5. Path \n
                    6. Erdos Renyi \n
                    7. Watts strogatz \n
                    8. Barabasi Albert \n
                    Even if this methods allow implementation with different agents, the previous restriction on the
                    number of agents force this arquitecture to consider only 6x6 matrixes.""")

        matrix_num = int(input("Select one of the previous adyacence matrixes: ")) - 1
        selecting_m = True
        while selecting_m:
            if matrix_num not in [0, 1, 2, 3, 4, 5, 6, 7]:
                print("Incorrect selection, try again")
                formation = input("Please, select one of the previous adyacence matrixes: ")
            else:
                print("adyacence matrix " + adyacence_options[matrix_num] + " was successfully choosed")
                selecting_m = False
        print("Beginning simulation with adyacence matrix " + adyacence_options[matrix_num] + " and formation " +
              formation_options[formation_num])

        matrix = obtain_predefined_model(adyacence_options[matrix_num], formation_options[formation_num], 1)
        model_used = obtain_predefined_model(adyacence_options[matrix_num], formation_options[formation_num], 2)
        save_model(matrix, model_used, colors)
        print('Model saved!')
        print("Executing station main file")
        execfile("run_station.py")



    elif second_selection == "2":
        print("""\n For defining the formation of the agents it is needed to the user to define the distance between
                  the agents. Note this definition can cause implementation problems as it might be ambigous so be 
                  aware of this before trying to run any new arquitecture""")

        model_used = generate_model()

        print("\n On the other hand, regarding the association matrix it must be " + str(N_max) + "x" + str(N_max) + """as
               it is determined by the total number of agents. Please, use the following format for developing such matrix:
               \n input: number, x_coor, y_coor \n
               PARAMETERS MUST BE SEPARATED BY A COMA (,). Number is the parameter which contains teh value that is going 
               to be replaced in the matrix. It can only contain 1 or 0 values. Finlly, x_coor and y_coor defines the 
               position the number is going to be placed and they can take values from 1 to """ + str(N_max))
        matrix = construct_personalized_matrix()
        save_model(matrix, model_used, colors)
        print('Model saved!')
        print("Executing station main file")
        execfile("run_station.py")


def start_sim():
    print("""\n In order to start simulation it is essential you run the run_node.py code in the raspberries or 
                the computer you are using as processing unit of single agents. There are two main processes this 
                platform allows to develop. You can both choose: \n
                a) Adyacence matrix: It defines the way each agent communicate among each other. This means the info.
                 it has access to. \n
                b) Formation: It defines the way the agents are going to configure though space on the testing platform \n
                This system allows both, the usage of some predefined adyacence matrix and formations or some defined by 
                the user. Please select the operation mode you are aiming to: """)
    print(""""-------------------------------------------------------------------------------- \n
              1. Predefined \n
              2. Personalized\n 
              3. Back to previous menu \n
              -------------------------------------------------------------------------------""")
    second_choice = input("Please, select one of the previous options: ")
    second_error = True

    while second_error:
        if second_choice not in ["1", "2", "3"]:
            print("Incorrect selection, try again")
            second_choice = input("Please, select one of the previous options: ")
        elif second_choice == "1":
            second_choice_fun(second_choice)
            second_error = False
        elif second_choice == "2":
            second_choice_fun(second_choice)
            second_error = False
        elif second_choice == "3":
            print("Returning to main manu...")
            second_error = False


def main():
    global pass_2
    global pass_3

    print("""Welcome! \n 
           This user interface was designed to provide aid in the process of using E-pucks robots for modeling different 
           dynamics and strategies. Furthermore, it allows the user to set different parmeters to personalize how these
           models are set and allow the study of different attacks on the robots. \n
           This software was developed under the DDDAS proyect by GIAP""")

    print(""" _______________________________________________________ \n 
                  1. General idea of the system \n
                  2. Calibrate camera filters \n
                  3. Set IP addresses for both E-puck and Raspberries \n
                  4. Set robot colors
                  5. Run simulation""")
    first_choice = input("Please, select one of the previous options: ")
    first_error = True
    pass_2 = True
    pass_3 = True

    while first_error:
        if first_choice not in ["1", "2", "3", "4", "5"]:
            print("Incorrect selection, try again")
            first_choice = input("Please, select one of the previous options: ")
        elif first_choice in ["1", "2", "3", "4"]:
            first_choice_option(first_choice)
            first_error = False
        elif first_choice == "5":
            print("You are ready to start simulation!")
            first_choice_option(first_choice)
            first_error = False

        else:
            print("Something has gone wrong, please try again: ")
            input("Press [ENTER] to continue...")
            first_error = False
    main()


if __name__ == "__main__":
    # Centinels are defined
    inserting_colors = True
    colors = []
    pass_2 = False
    pass_3 = False

    main()
