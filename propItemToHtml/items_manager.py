from collections import OrderedDict 

'''
    This file gives useful functions to read propItem.txt files
'''

NUMBER_OF_PARAMS = 6
ITEM_MANAGER = None

ITEM_REGEX = "([A-Za-z0-9_]+)"

# Gives the right item manager to your number of parameters. You can not store it, as it will be
# reminded by other functions, but you need to call it once if your number of dw param is different than 6
def get_item_manager(number_of_parameters=6):
    global ITEM_MANAGER
    global NUMBER_OF_PARAMS
    
    if ITEM_MANAGER is None or NUMBER_OF_PARAMS != number_of_parameters:
        NUMBER_OF_PARAMS = number_of_parameters
    
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
        item_manager = get_item_manager()
    
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
def get_item_list(propItem_path, item_manager=ITEM_MANAGER):
    if item_manager is None:
        item_manager = get_item_manager()

    items = OrderedDict()

    with open(propItem_path, encoding="ansi") as f:
        for line in f.readlines():
            item = decrypt_item(line, item_manager)
            if item is not None:
                items[item['ID']] = item
            
    return items


if __name__ == '__main__':
    print(get_item_list("..\\..\\FlyFF-VS17\\Resource\\propItem.txt"))