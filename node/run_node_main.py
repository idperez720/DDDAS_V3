
import os
from main_node import *
from main_node_attack import * 

def run_attacked(dir):
    main_node()

def run_regular(dir):
    main_atack()

def main():
    selecting = True

    dir = os.path.dirname(os.path.abspath(__file__))

    while selecting:
        print("""\n Welcome! 
                    1. Run regular node \n
                    2. Run attacked node""")
        selection = int(input("Select one of the previous options: "))

        if selection not in [1, 2]:
            print("Incorrect selection, try again")
            formation = input("Please, select one of the previous formations: ")
        elif selection == 1:
            run_regular(dir)
        else:
            run_atacked(dir)

if __name__ == "__main__":
    main()
