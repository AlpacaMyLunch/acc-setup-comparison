import json, re
from os import path
from attr import attributes
from deepdiff import DeepDiff


class Setup:
    file_path: str
    file_name: str
    attributes: dict

    def __init__(self, file_path: str):
        
        self.file_path = file_path
        self.file_name = path.basename(file_path)

        # Load the JSON data 
        self.attributes = {}
        self.load_data(file_path)
        self.attributes['temperatures'] = self.parse_title()

        print()
        print(self.attributes['carName'], self.file_name)


        self.convert_values()

        

        
    def parse_title(self) -> dict:
        """
        Expect the ambient and track temperature in the title.
        a27 t33
        """

        output = {}

        temperature_pattern = '[a,t]{1}[0-9]{2}'
        temps = re.findall(temperature_pattern, self.file_name.lower())
        

        for temp in temps:

            # Ambient temperature
            if temp[0] == 'a':
                output['ambient'] = temp[1:]

            # Track temperature
            elif temp[0] == 't':
                output['track'] = temp[1:]

        return output


    def load_data(self, file_path: str) -> dict:
        

        data = json_from_file(file_path)

        self.attributes['carName'] = data['carName']

        basic = data['basicSetup']

        tires = basic['tyres']
        self.attributes['tyreCompound'] = tires['tyreCompound']
        self.attributes['tyrePressure'] = parse_corner_values(tires['tyrePressure'])

        alignment = basic['alignment']
        self.attributes['camber'] = parse_corner_values(alignment['camber'])
        self.attributes['toe'] = parse_corner_values(alignment['toe'])
        self.attributes['staticCamber'] = parse_corner_values(alignment['staticCamber'])
        self.attributes['toeOutLinear'] = parse_corner_values(alignment['toeOutLinear'])
        self.attributes['caster'] = {
            'left front': alignment['casterLF'],
            'right front': alignment['casterRF']
        }
        self.attributes['steerRatio'] = alignment['steerRatio']

        electronics = basic['electronics']
        self.attributes['tc1'] = electronics['tC1']
        self.attributes['tc2'] = electronics['tC2']
        self.attributes['abs'] = electronics['abs']
        self.attributes['ecuMap'] = 1 + electronics['eCUMap']

        advanced = data['advancedSetup']

        mechanical = advanced['mechanicalBalance']
        self.attributes['arbFront'] = mechanical['aRBFront']
        self.attributes['arbRear'] = mechanical['aRBRear']
        self.attributes['wheelRate'] = parse_corner_values(mechanical['wheelRate'])
        self.attributes['bumpStopRateUp'] = parse_corner_values(mechanical['bumpStopRateUp'])
        self.attributes['bumpStoppRateDn'] = parse_corner_values(mechanical['bumpStopRateDn'])
        self.attributes['bumpStopWindow'] = parse_corner_values(mechanical['bumpStopWindow'])
        self.attributes['brakeTorque'] = mechanical['brakeTorque']
        self.attributes['brakeBias'] = mechanical['brakeBias']

        dampers = advanced['dampers']
        self.attributes['bumpSlow'] = parse_corner_values(dampers['bumpSlow'])
        self.attributes['bumpFast'] = parse_corner_values(dampers['bumpFast'])
        self.attributes['reboundSlow'] = parse_corner_values(dampers['reboundSlow'])
        self.attributes['reboundFast'] = parse_corner_values(dampers['reboundFast'])

        aero = advanced['aeroBalance']
        self.attributes['rideHeight'] = {
            'front': aero['rideHeight'][0],
            'rear': aero['rideHeight'][2]
        }
        self.attributes['splitter'] = aero['splitter']
        self.attributes['rearWing'] = aero['rearWing']
        self.attributes['brakeDuct'] = {
            'front': aero['brakeDuct'][0],
            'rear': aero['brakeDuct'][1]
        }

        drivetrain = advanced['drivetrain']
        self.attributes['preload'] = drivetrain['preload']

    def convert_values(self):
        """
        convert the raw setup values to more readable values
        """



        for key in self.attributes['tyrePressure']:
            new_val = tire_pressure_conversion(self.attributes['tyrePressure'][key])
            self.attributes['tyrePressure'][key] = new_val


        self.attributes['toe'] = toe_conversion(self.attributes['toe'], self.attributes['carName'])




def parse_corner_values(vals: list) -> dict:
    """
    Take the array of tire/corner values and return a more descriptive dict
    Use for tire pressure, camber, toe,...
    """

    # Need to verify which index goes to which tire.
    return {
        'front_left': vals[0],
        'front_right': vals[1],
        'rear_left': vals[2],
        'rear_right': vals[3]
    }


def tire_pressure_conversion(raw: int) -> float:
    # raw 53 = display 25.6
    # raw 57 = display 26.0

    away_from_57 = raw - 57
    return float(
        26.0 + (away_from_57 / 10)
    )


def toe_conversion(raw: dict, car_name: str) -> float:
    
    if car_name == 'mclaren_720s_gt3':

        for front in ['front_left', 'front_right']:
            raw[front] = -0.48 + (0.01 * raw[front])
        for rear in ['rear_left', 'rear_right']:
            raw[rear] = -0.1 + (0.01 * raw[rear])

    elif car_name in ['nissan_gt_r_gt3_2018', 'bmw_m6_gt3', 'nissan_gt_r_gt3_2017', 'bmw_m4_gt3', 'bmw_m4_gt4', 'chevrolet_camaro_gt4r', 'mercedes_amg_gt4']:
        
        for front in ['front_left', 'front_right']:
            raw[front] = -0.2 + (0.01 * raw[front])
        for rear in ['rear_left', 'rear_right']:
            raw[rear] = 0.01 * raw[rear]
        
    else:

        for corner in ['front_left', 'front_right', 'rear_left', 'rear_right']:
            raw[corner] = 0.01 * raw[corner] - 0.4




    for corner in ['front_left', 'front_right', 'rear_left', 'rear_right']:
        raw[corner] = round(raw[corner], 2)

    return raw
    

def caster_conversion(raw: int) -> float:
    # raw 23 = display 13.8
    # raw 3 = display 11.2
    # raw 46 = display 12.3


    pass


def json_from_file(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data

def json_to_file(file_name, json_data):
    with open(file_name, 'w') as out_file:
        json.dump(json_data, out_file)

