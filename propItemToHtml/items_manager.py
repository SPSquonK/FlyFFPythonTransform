import re
from collections import OrderedDict 
import os

'''
    This file gives useful functions to read propItem.txt files
'''

configuration = None

NUMBER_OF_PARAMS = 6
ITEM_MANAGER = None

ITEM_REGEX = "([A-Za-z0-9_]+)"
THIS_DIR = os.path.dirname(os.path.abspath(__file__)) + "\\"


def getPropItemPath():
    global configuration
    load_configuration()
    return configuration['path'] + configuration['propItem']


def path():
    global configuration
    load_configuration()
    return configuration['path']


def nb_param():
    global configuration
    load_configuration()
    return configuration['propItemParameters']


def modifiedPropItem():
    global configuration
    load_configuration()
    
    return getPropItemPath() if configuration['modifyInPlace'] else THIS_DIR + configuration['propItem']


def adjustForLEVTSZF():
    global configuration
    load_configuration()
    return configuration['LEVTSZF']
    

def load_configuration():
    global configuration
    if configuration is not None:
        return
        
    configuration = {}

    # Read file
    with open("config.txt") as f:
        for line in f.readlines():
            if line.startswith("//"):
                continue
            
            m = re.match("([A-Za-z]*) = (.*)$", line)
            
            if m is None:
                continue
                
            field = m.group(1)
            value = m.group(2)
            
            if field == "path":
                configuration['path'] = value.strip()
            elif field == "propItem":
                configuration['propItem'] = value.strip()
            elif field == "propItemParameters":
                NUMBER_OF_PARAMS = int(value)
            elif field == "modifyInPlace":
                configuration['modifyInPlace'] = value == "True"
            elif field == "legendaryemeraldvolcanoterrasunzeroflyff"
                configuration['LEVTSZF'] = value == "True"
            
    # Normalize configuration
    default_values = {
        "path": "..\\..\\FlyFF-VS17\\Resource\\",
        "propItem": "propItem.txt",
        "propItemParameters": 6,
        "modifyInPlace": True,
        "LEVTSZF": False
    }
    
    for default_value_type in default_values:
        if default_value_type not in configuration or configuration[default_value_type] == "":
            configuration[default_value_type] = default_values[default_value_type]
    
    print(configuration)
    
    if configuration['path'][-1] != "\\" and configuration['path'][-1] != "/":
        configuration['path'] = configuration['path'] + "\\"
    
    # Force reload
    global ITEM_MANAGER
    ITEM_MANAGER = None
    get_item_manager()

# Gives the right item manager to your number of parameters. You can not store it, as it will be
# reminded by other functions, but you need to call it once if your number of dw param is different than 6
def get_item_manager():
    global ITEM_MANAGER
    
    if ITEM_MANAGER is None:
        number_of_parameters = configuration['propItemParameters']
    
        ITEM_MANAGER = {
            'ID': 1,
            'IDS_WEAPON_NAME': 2,
            'IK3': 7,
            'JOB': 8,
            'DOUBLE_HANDED': 16,
            'START_DW_PARAM': 53,
            'START_ADJ_PARAM': 53 + number_of_parameters,
            'SZICON': 132 - (6 - number_of_parameters) * 4,
            'LEVEL': 128 - (6 - number_of_parameters) * 4,
            'LEN_DW_PARAM': number_of_parameters,
            'EXPECTED_LENGTH': 136 - (6 - number_of_parameters) * 4 
        }

    return ITEM_MANAGER


# Decrypt an item with the line in propItem. You can 
def decrypt_item(line, item_manager=ITEM_MANAGER):
    if item_manager is None:
        load_configuration()
        item_manager = ITEM_MANAGER
    
    line = line.strip().replace(str(chr(10)), "").replace("\r", "")
    
    if line is None or line.startswith("//"):
        return None
    
    parameters_list = line.split("\t")
    
    if len(parameters_list) != item_manager['EXPECTED_LENGTH']:
        return None
    
    bonus = []
    for i in range(item_manager['LEN_DW_PARAM']):
        bonus_type = parameters_list[item_manager['START_DW_PARAM'] + i].strip()
        bonus_quantity = parameters_list[item_manager['START_ADJ_PARAM'] + i].strip()
        
        if bonus_type == "=":
            continue
        
        bonus.append((bonus_type, bonus_quantity))
    
    return {
        'ID': parameters_list[item_manager['ID']],
        'TXT_NAME': parameters_list[item_manager['IDS_WEAPON_NAME']],
        'IK3': parameters_list[item_manager['IK3']],
        'JOB': parameters_list[item_manager['JOB']],
        'DOUBLE_HANDED': parameters_list[item_manager['DOUBLE_HANDED']] == 'HD_TWO',
        'ICON_IMAGE': parameters_list[item_manager['SZICON']].replace("\"", ""),
        'Level': 0 if parameters_list[item_manager['LEVEL']] == "=" else int(parameters_list[item_manager['LEVEL']]),
        'Bonus': bonus
    }


# Gives an ordered dictionnary with every items in propItem
def get_item_list(propItem_path=None, item_manager=ITEM_MANAGER):
    if item_manager is None:
        load_configuration()
        item_manager = ITEM_MANAGER
        
    if propItem_path is None:
        propItem_path = getPropItemPath()

    items = OrderedDict()

    with open(propItem_path, encoding="ansi") as f:
        for line in f.readlines():
            item = decrypt_item(line, item_manager)
            if item is not None:
                items[item['ID']] = item
            
    return items


if __name__ == '__main__':
    load_configuration()
    print(get_item_list())