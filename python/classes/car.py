from os import path, listdir
from .setup import Setup

HOME_DIR = path.expanduser('~')
SETUP_DIR = HOME_DIR + '\Documents\Assetto Corsa Competizione\Setups\\'

class Car:
    directory: str 
    name: str
    setups: dict
    tracks: list

    def __init__(self, compressed_name: str):

        self.directory = SETUP_DIR + compressed_name + '\\'
        self.name = compressed_name.replace('_', ' ')


        # Load the tracks
        self.tracks = self.gather_track_list()

        # Load the setup files
        self.setups = {}
        for track in self.tracks:
            self.setups[track] = {}
            for file_name in self.gather_setups(track):
                setup = Setup('{}{}\{}'.format(self.directory, track, file_name))
                self.setups[track][file_name] = setup



    def gather_track_list(self) -> list:
        return listdir(self.directory)

    def gather_setups(self, track: str) -> list:
        return listdir(self.directory + track)