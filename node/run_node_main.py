
import os
from run_node import *
from run_node_attacked import * 

def run_attacked():
    main_atack()

def run_regular():
    main_node()

def main():
    selecting = True
    while selecting:
        print("""\n Welcome! 
                    1. Run regular node \n
                    2. Run attacked node""")
        selection = int(input("Select one of the previous options: "))

        if selection not in [1, 2]:
            print("Incorrect selection, try again")
            formation = input("Please, select one of the previous formations: ")
        elif selection == 1:
            run_regular()
        else:
            run_attacked()

if __name__ == "__main__":
    main()
