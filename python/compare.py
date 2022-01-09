from os import path, listdir
from classes.car import Car
from classes.setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'
VEHICLE_LIST = listdir(SETUP_DIR)







def main():
    
    a = Setup('C:\\Users\\micha\\Documents\\Assetto Corsa Competizione\\Setups\\bentley_continental_gt3_2018\\monza\\a16 t22.json')
    b = Setup('C:\\Users\\micha\\Documents\\Assetto Corsa Competizione\\Setups\\bentley_continental_gt3_2018\\monza\\a21.t27-150.5.json')
    comparison = a.compare(b)




if __name__ == '__main__':
    main()