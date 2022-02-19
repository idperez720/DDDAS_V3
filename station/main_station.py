import sys

import numpy as np
from detection.calibrate_colors import main_calibrate_colors
from communication.blink_to_identify import main_blink_to_identify

sys.path.append("./")

def input_colors(N):
    print("Please, enter the name of the color that identify each robot you are working with")
    colors = np.array([])
    inserting = True
    i = 0
    while inserting:
        color = input("Input a new color: ")
        if color not in colors:
            colors.append(color)
            i += 1
        else:
            print("Color already added!")

        if i == N:
            break
    return  colors

def first_choice_option(first_choice):
    if first_choice == "1":
        print("""The system consists in 4 main devices: The camera, the main station, the raspberries and the E-puck.
                  Each is essential for the correct development of different simulation strategies. In general, 
                  communication protocols are based on the main station, this is the computer were you are running this
                  code. The camera connects the main station through a server that allows the main station to calculate
                  the position of the robots that are set in the platform you are using. In general it is required that
                  such platform has: \n 1. Defined area limits \n 2. Constant illumination thoughtout its surfce \n 
                  3. Different color from the ones used to identify the robots \n In general it is further recommended 
                  to notice different colors next to the platforms from other objects such as tapes placed omn the floor,
                  or different objects. These objects must be covered, otherwise the system will not work appropiately. \n \n
                  Regarding the other devices, the purpose of this platform is to allow the simulation and physical 
                  implementation of descentrilized systems which means the user can define how communication interaction actually
                  happen. This means Raspberrys are the ones that compute their own dynamics and though client-server 
                  scheme obtain information about their position and the ones they can communicate with through the main 
                  station. Finlly, raspberries control the robors. \n \n For further info go to the read me file. """)
        input("Press [ENTER] to continue...")
    elif first_choice == "2":
        print("""Camara filters calibration requires platform requirements discussed on on General idea of the system. 
                 As HSV color space is used,so any missing requirement may led the system to fail, so be aware of this possibility
                 before continuing... """)
        input("Press [ENTER] to continue...")
        print("""Initializing... \n Select a region of the camera image in the color that identifies each robot""")
        main_calibrate_colors("calibrate")
        print("""Calibration developed succesfully! Before continuing it is recommended to further develop a debug 
                 process. The circles with representative color of each robot should be seen surrounded by a green line.
                  If anythings seems odd, then you should consider perform again calibration process. Do you want to 
                  start the debug process?""")
        answer = input("y/n: ")
        asking = True
        while asking:
            if answer not in ["y", "n", "yes", "not"]:
                print("Incorrect selection, try again")
                answer = input("y/n: ")
            elif answer == "y" or answer == "yes":
                main_calibrate_colors("not_calibrate")
            else:
                break
        print("Returning to main section...")
        input("Press [ENTER] to continue...")
    elif first_choice == "3":
        print("""In order to set IP addresses and associate each Raspberry with an E-puck robot first you have to 
                 connect them all to the same wifi network and be aware of their respective IP address. This might 
                 seem challenging at first, but raspberries can implement a protocol called SSH so that you can run 
                 code and have general access to its system remotely from another computer. It is further recommended
                 you run each raspberry on a different console to ease the whole process of simulation and physical
                 implementation. If you are using a computir with some linux distribution some commands such as nmap 
                 might be particularly useful as well as using each raspberry's localhost name. \n On the other hand, if
                  you have doubts on how to connect E-puck robots to a wifi network you might find this guide useful:
                   https://www.gctronic.com/doc/index.php/e-puck2 \n \n Once this is done and you have clear each IP 
                   address you might continue...""")
        input("Press [ENTER] to continue...")

        inserting = True

        while inserting:

            N = int(input("Input the number of robots to identify: "))
            N_max = int(input("Input the total number of robots you are currently working with: "))
            if N_max < N:
                print("Total number of robots can not be greater than the number of robots to identify!!")
                pass

            colors = input_colors(N)
            break

        main_blink_to_identify(colors, N, N_max)
        print("All robots identified and associated with a raspberry successfully. Returning to main section...")
        input("Press [ENTER] to continue...")

def main():

    global pass_2
    global pass_3

    print("""Welcome! \n 
           This user interface was designed to provide aid in the process of using E-pucks robots for modeling different 
           dynamics and strategies. Furthermore, it allows the user to set different parmeters to personalize how these
           models are set and allow the study of different attacks on the robots. \n
           This software was developed under the DDDAS proyect by GIAP""")

    print(""" 1. General idea of the system \n
              2. Calibrate camara filters \n
              3. Set IP addresses for both E-puck and Raspberries \n
              4. Run simulation""")

    first_choice = input("Please, select one of the previous options: ")
    first_error = True

    while first_error:
        if first_choice not in ["1", "2", "3", "4"]:
            print("Incorrect selection, try again")
            first_choice = input("Please, select one of the previous options: ")
        elif first_choice == "1":
            first_choice_option(first_choice)
        elif first_choice == "2":
            first_choice_option(first_choice)
            pass_2 = True
            print(""" 1. General idea of the system \n
                          2. Calibrate camara filters \n
                          3. Set IP addresses for both E-puck and Raspberries \n
                          4. Run simulation""")
            input("Please, select one of the previous options: ")
        elif first_choice == "3":
            first_choice_option(first_choice)
            pass_3 = True
            print(""" 1. General idea of the system \n
                          2. Calibrate camara filters \nj
                          3. Set IP addresses for both E-puck and Raspberries \nj
                          4. Run simulation""")
            first_choice = input("Please, select one of the previous options: ")
        else:
            if pass_2 and pass_3 and first_choice == "4":
                print("You are ready to start simulation!")
                first_choice_option(first_choice)
                first_error = False
            elif not pass_2:
                print("Camara filter calibration is missing!")
                input("Press [ENTER] to continue...")
                print(""" 1. General idea of the system \n
                              2. Calibrate camara filters \n
                              3. Set IP addresses for both E-puck and Raspberries \n
                              4. Run simulation""")
                first_choice = input("Please, select one of the previous options: ")
            elif not pass_3:
                print("Raspberry and e-puck IPs weren't setted...")
                input("Press [ENTER] to continue...")
                print(""" 1. General idea of the system \n
                              2. Calibrate camara filters \n
                              3. Set IP addresses for both E-puck and Raspberries \n
                              4. Run simulation""")
                first_choice = input("Please, select one of the previous options: ")
            else:
                print("Something has gone wrong, please try again: ")
                print(""" 1. General idea of the system \n
                                              2. Calibrate camara filters \n
                                              3. Set IP addresses for both E-puck and Raspberries \n
                                              4. Run simulation""")
                first_choice = input("Please, select one of the previous options: ")

if __name__ == "__main__":
    #Centinels are defined
    pass_2 = False
    pass_3 = False

    main()
