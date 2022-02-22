
import os

def run_attacked(dir):
    exec(dir + "/run_node.py")

def run_regular(dir):
    exec(dir + "/run_node.py")

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
