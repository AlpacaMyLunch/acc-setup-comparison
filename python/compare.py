import json
from PyInquirer import prompt
from os import path, listdir
from classes.car import Car
from classes.setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'
VEHICLE_DIRECTORIES = listdir(SETUP_DIR)
vehicle_list = {}



def return_car(name: str) -> Car:
    for car in vehicle_list: 
        if car == name:
            return vehicle_list[car]

    return None

def return_setup(car: Car, track: str, name: str) -> Setup:
    for setup in car.setups[track]:
        if setup == name: 
            return car.setups[track][setup]

    return None

def prompt_car() -> Car:
    question_car = {
            'type': 'list',
            'name': 'car',
            'message': 'Select a car',
            'choices': list(vehicle_list.keys())
        }

    answer_car = prompt(question_car)
    return return_car(answer_car['car'])

def prompt_track(car: Car) -> str:
    question_track =  {
        'type': 'list',
        'name': 'track',
        'message': 'Select a track',
        'choices': car.tracks
    }
    
    answer_track = prompt(question_track)
    return answer_track['track']


def prompt_setup(car: Car, track: str, omit: Setup = None) -> Setup:

    display_setups = []
    if omit:
        for setup in car.setups[track]:
            if setup != omit.file_name:
                display_setups.append(setup)
    else:
        display_setups = car.setups[track]

    question_setup = {
        'type': 'list',
        'name': 'setup',
        'message': 'Select a setup',
        'choices': display_setups
    }
    
    answer_setup = prompt(question_setup)
    return return_setup(
        car,
        track,
        answer_setup['setup']
    )


def main():
    global vehicle_list

    for name in VEHICLE_DIRECTORIES:
        car = Car(name)
        vehicle_list[car.name] = car

    selected_car = prompt_car()

    selected_track = prompt_track(selected_car)

    selected_setup_1 = prompt_setup(selected_car, selected_track)
    
    selected_setup_2 = prompt_setup(selected_car, selected_track, selected_setup_1)
    
    comparison = selected_setup_1.compare(selected_setup_2)

    print(
        json.dumps(
            comparison,
            indent=4
        )
    )


    


if __name__ == '__main__':
    main()