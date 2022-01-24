import json, re
from os import path


CORNER_NAMES = ['front_left', 'front_right', 'rear_left', 'rear_right']

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

        Math copied from this tool: https://simsource.azurewebsites.net/tools/setup-diff
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


def toe_conversion(raw: dict, car_name: str) -> dict:
    
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

        for corner in CORNER_NAMES:
            raw[corner] = 0.01 * raw[corner] - 0.4




    for corner in CORNER_NAMES:
        raw[corner] = round(raw[corner], 2)

    return raw
    

def caster_conversion(raw: dict, car_name: str) -> dict:
    
    if car_name in ['ferrari_488_gt3', 'ferrari_488_gt3_evo']:
        for corner in CORNER_NAMES:
            raw[corner] = (0.159 * raw[corner]) + 5
    
    elif car_name in ['audi_r8_lms', 'audi_r8_lms_evo']:
        for corner in CORNER_NAMES:
            raw[corner] = 8.8 + raw[corner] * (8 / 34)

    elif car_name in ['lamborghini_huracan_gt3', 'lamborghini_huracan_gt3_evo']:
        for corner in CORNER_NAMES:
            raw[corner] = 6.2 + raw[corner] * (8.8 / 34)

    elif car_name == 'mclaren_650s_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 5.3 + (.24 * raw[corner])

    elif car_name == 'nissan_gt_r_gt3_2018':
        for corner in CORNER_NAMES:
            raw[corner] = 12.5 + (.18 * raw[corner])

    elif car_name == 'bmw_m6_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 6.7 + raw[corner] * (8.3 / 40)

    elif car_name in ['bentley_continental_gt3_2018', 'bentley_continental_gt3_2016']:
        for corner in CORNER_NAMES:
            raw[corner] = 8.3 + raw[corner] * (7.2 / 30)

    elif car_name in ['porsche_991ii_gt3_cup', 'porsche_991_gt3_r']:
        for corner in CORNER_NAMES:
            raw[corner] = 7.3 + (.1 * raw[corner])

    elif car_name == 'nissan_gt_r_gt3_2017':
        for corner in CORNER_NAMES:
            raw[corner] = 6 + raw[corner] * (11.3 / 60)

    elif car_name == 'amr_v12_vantage_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 8.3 + (.22 * raw[corner])

    elif car_name == 'lamborghini_gallardo_rex':
        for corner in CORNER_NAMES:
            raw[corner] = 4.9 + raw[corner] * (7.1 / 34)

    elif car_name == 'jaguar_g3':
        for corner in CORNER_NAMES:
            raw[corner] = 4 + (.1825 * raw[corner])

    elif car_name == 'lexus_rc_f_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 7.9 + (.19 * raw[corner])

    elif car_name in ['honda_nsx_gt3', 'honda_nsx_gt3_evo']:
        for corner in CORNER_NAMES:
            raw[corner] = 8.8 + (raw[corner] * (6.4 / 34))

    elif car_name == 'lamborghini_huracan_st':
        for corner in CORNER_NAMES:
            raw[corner] = 6.2 + raw[corner] * (8.8 / 34)

    elif car_name in ['mercedes_amg_gt3', 'mercedes_amg_gt3_evo']:
        for corner in CORNER_NAMES:
            raw[corner] = 6 + raw[corner] * (8.1 / 44)

    elif car_name == 'amr_v8_vantage_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 10.7 + raw[corner] * (5.4 / 30)

    elif car_name == 'mclaren_720s_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 5.3 + raw[corner] * (2.7 / 11)

    elif car_name == 'porsche_991ii_gt3_r':
        for corner in CORNER_NAMES:
            raw[corner] = 4.4 + .2 * raw[corner]

    elif car_name == 'bmw_m4_gt3':
        for corner in CORNER_NAMES:
            raw[corner] = 6.1 + .195 * raw[corner]

    elif car_name == 'alpine_a110_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 7.3 + raw[corner] * (6.4 / 34)

    elif car_name == 'amr_v8_vantage_gt4':
        for corner in CORNER_NAMES:
            raw[corner] =  10.7 + raw[corner] * (5.4 / 30)

    elif car_name == 'audi_r8_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 6.6 + raw[corner] * (6.7 / 34)

    elif car_name == 'bmw_m4_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 8.4 # ???????????????????

    elif car_name == 'chevrolet_camaro_gt4r':
        for corner in CORNER_NAMES:
            raw[corner] = 7.1 # ????????????????????

    elif car_name == 'ginetta_g55_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 3.7 + .2625 * raw[corner]

    elif car_name == 'ktm_xbow_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 1.7 + .1925 * raw[corner]

    elif car_name == 'maserati_mc_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 3.4 + raw[corner] * (2.2 / 10)

    elif car_name == 'mclaren_570s_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 5.3 + raw[corner] * (4.9 / 20)

    elif car_name == 'mercedes_amg_gt4':
        for corner in CORNER_NAMES:
            raw[corner] = 9.2 + .18 * raw[corner]

    elif car_name == 'porsche_718_cayman_gt4_mr':
        for corner in CORNER_NAMES:
            raw[corner] = 7.3 + raw[corner] * (2.9 / 28)

    return raw


def brake_bias_conversion(raw: int, car_name: str) -> float:

    if car_name in ['ferrari_488_gt3', 'mclaren_650s_gt3', 'mclaren_720s_gt3', 'ferrari_488_gt3_evo', 'chevrolet_camaro_gt4r']:
        return 47 + .2 * raw

    if car_name in ['audi_r8_gt4', 'mercedes_amg_gt3_evo', 'honda_nsx_gt3_evo', 'audi_r8_lms_evo', 'lamborghini_huracan_gt3_evo', 'mercedes_amg_gt3', 'audi_r8_lms', 'lamborghini_huracan_gt3', 'lamborghini_gallardo_rex', 'lexus_rc_f_gt3', 'honda_nsx_gt3', 'lamborghini_huracan_st']:
        return 50 + .2 * raw

    if car_name in ['nissan_gt_r_gt3_2017', 'nissan_gt_r_gt3_2018', 'bmw_m6_gt3']:
        return 47.5 + .3 * raw

    if car_name in ['amr_v8_vantage_gt3', 'bentley_continental_gt3_2016', 'bentley_continental_gt3_2018', 'amr_v12_vantage_gt3', 'jaguar_g3']:
        return 57 + .2 * raw
    
    if car_name in ['porsche_991ii_gt3_cup', 'bmw_m4_gt4', 'maserati_mc_gt4']:
        return 49 + .2 * raw

    if car_name in ['porsche_991_gt3_r', 'porsche_991ii_gt3_r']:
        return 43 + .2 * raw

    if car_name == 'bmw_m4_gt3':
        return 48.5 + .3 * raw
    
    if car_name in ['alpine_a110_gt4', 'amr_v8_vantage_gt4', 'porsche_718_cayman_gt4_mr']:
        return 45 + .2 * raw

    if car_name in ['ginetta_g55_gt4']:
        return 46 + .2 * raw

    if car_name in ['ktm_xbow_gt4']:
        return 44 + .2 * raw

    if car_name == 'mclaren_570s_gt4':
        return 60 + .2 * raw

    if car_name == 'mercedes_amg_gt4':
        return 51 + .2 * raw

    
    

def json_from_file(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data

def json_to_file(file_name, json_data):
    with open(file_name, 'w') as out_file:
        json.dump(json_data, out_file)

