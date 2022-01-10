from PyInquirer import prompt
from os import path, listdir
from classes.car import Car
from classes.setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'
VEHICLE_LIST = listdir(SETUP_DIR)



def return_car(name: str, cars: dict) -> Car:
    for car in cars: 
        if car == name:
            return cars[car]

    return None


def return_setup(car: Car, track: str, name: str) -> Setup:
    for setup in car.setups[track]:
        if setup == name: 
            return car.setups[track][setup]

    return None

def main():
    
    cars = {}
    for name in VEHICLE_LIST:
        car = Car(name)
        cars[car.name] = car

    question_car = {
            'type': 'list',
            'name': 'car',
            'message': 'Select a car',
            'choices': list(cars.keys())
        }
    

    answer_car = prompt(question_car)
    selected_car = return_car(answer_car['car'], cars)

    question_track =  {
        'type': 'list',
        'name': 'track',
        'message': 'Select a track',
        'choices': selected_car.tracks
    }
    
    answer_track = prompt(question_track)
    selected_track = answer_track['track']

    question_setup_1 = {
        'type': 'list',
        'name': 'setup_1',
        'message': 'Select the first setup',
        'choices': selected_car.setups[selected_track]
    }
    
    answer_setup_1 = prompt(question_setup_1)
    selected_setup_1 = return_setup(
        selected_car,
        selected_track,
        answer_setup_1['setup_1']
    )

    question_setup_2 = {
        'type': 'list',
        'name': 'setup_2',
        'message': 'Select the first setup',
        'choices': selected_car.setups[selected_track]
    }
    
    answer_setup_2 = prompt(question_setup_2)
    selected_setup_2 = return_setup(
            selected_car,
            selected_track,
            answer_setup_2['setup_2']
        )

    
    comparison = selected_setup_1.compare(selected_setup_2)

    print(comparison)


    


if __name__ == '__main__':
    main()