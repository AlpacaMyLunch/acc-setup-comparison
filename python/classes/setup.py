import json, re
from os import path
from deepdiff import DeepDiff


class Setup:
    file_path: str
    file_name: str
    attributes: dict

    def __init__(self, file_path: str):
        
        self.file_path = file_path
        self.file_name = path.basename(file_path)

        # Load the JSON data 
        self.attributes = json_from_file(file_path)
        self.attributes['temperatures'] = self.parse_title()



        
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

    def compare(self, other_setup) -> dict:

        """
        Find and return what is different between two car setups
        """

        differences = DeepDiff(self.attributes, other_setup.attributes)['values_changed']

        output = {}

        for difference in differences:

            setup_items = []
            for item in re.findall("\[([A-Za-z0-9_']+)\]", difference):

                # My RegEx is lacking.  Need to remove the single quote
                item = item.replace("'", "")

                # also if the last item is numeric that means it is an index to a list.
                # ignore the list index, return the parent
                if item.isnumeric() == False:
                    setup_items.append(item)



            nested_set(
                output, 
                setup_items, 
                {
                    self.file_name: nested_get(self.attributes, setup_items),
                    other_setup.file_name: nested_get(other_setup.attributes, setup_items),
                }
            ) 


        # Parse some of the output
        if 'basicSetup' in output:
            if 'tyres' in output['basicSetup']:
                if 'tyrePressure' in output['basicSetup']['tyres']:
                    for file_name in output['basicSetup']['tyres']['tyrePressure']:
                        output['basicSetup']['tyres']['tyrePressure'][file_name] = parse_tire_values(output['basicSetup']['tyres']['tyrePressure'][file_name])

            if 'alignment' in output['basicSetup']:
                if 'staticCamber' in output['basicSetup']['alignment']:
                    for file_name in output['basicSetup']['alignment']['staticCamber']:
                        output['basicSetup']['alignment']['staticCamber'][file_name] = parse_tire_values(output['basicSetup']['alignment']['staticCamber'][file_name])
                if 'toeOutLinear' in output['basicSetup']['alignment']:
                    for file_name in output['basicSetup']['alignment']['toeOutLinear']:
                        output['basicSetup']['alignment']['toeOutLinear'][file_name] = parse_tire_values(output['basicSetup']['alignment']['toeOutLinear'][file_name])


        if 'advancedSetup' in output:
            if 'aeroBalance' in output['advancedSetup']:
                if 'rodLength' in output['advancedSetup']['aeroBalance']:
                    for file_name in output['advancedSetup']['aeroBalance']['rodLength']:
                        output['advancedSetup']['aeroBalance']['rodLength'][file_name] = parse_tire_values(output['advancedSetup']['aeroBalance']['rodLength'][file_name])
        return output


def parse_tire_values(tires: list) -> dict:
    """
    Take the array of tire values and return a more descriptive dict
    Use for tire pressure, camber, toe, caster...
    """

    # Need to verify which index goes to which tire.
    # this is a guess
    return {
        'front_left': tires[0],
        'front_right': tires[1],
        'rear_right': tires[2],
        'rear_left': tires[3]
    }


def json_from_file(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data

def json_to_file(file_name, json_data):
    with open(file_name, 'w') as out_file:
        json.dump(json_data, out_file)

def nested_get(data, keys):

    # if the last key is numeric, it is an index to an array
    # remove it and return the whole array

    last_key = keys[-1]
    if last_key.isnumeric():
        keys = keys[:-1]

    for key in keys:
        data = data[key]
    return data

def nested_set(data, keys, val):
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = val