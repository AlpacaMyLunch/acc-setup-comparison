from os import path, listdir
from classes.car import Car
from classes.setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'
VEHICLE_LIST = listdir(SETUP_DIR)







def main():
    
    cars = []
    for name in VEHICLE_LIST:
        car = Car(name)
        print(car.name)
        print(car.tracks)
        print()




if __name__ == '__main__':
    main()