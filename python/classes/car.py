from os import path, listdir
from .setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'

class Car:
    directory: str 
    name: str
    setups: dict

    def __init__(self, compressed_name: str):

        self.directory = SETUP_DIR + compressed_name + '/'
        self.name = compressed_name.replace('_', ' ')


        # Load the setup files
        self.setups = {}
        for track in self.gather_track_list():
            self.setups[track] = {}
            for file_name in self.gather_setups(track):
                setup = Setup(self.directory + '/' + file_name)
                self.setups[track][file_name] = setup



    def gather_track_list(self) -> list:
        return listdir(self.directory)

    def gather_setups(self, track: str) -> list:
        return listdir(self.directory + track)