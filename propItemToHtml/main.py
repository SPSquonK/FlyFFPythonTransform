import sys
from collections import OrderedDict 

path = "..\\..\\FlyFF-VS17\\Resource\\" if len(sys.argv) < 2 else sys.argv[1]
propItem_filename = "propItem.txt" if len(sys.argv) < 3 else sys.argv[2]
number_of_parameters = 6 if len(sys.argv) < 4 else sys.argv[3]

weapons_type = OrderedDict()

def add_types(dict, list):
    for item in list:
        dict[item] = []

add_types(weapons_type, ['IK3_SWORD', 'IK3_AXE', 'IK3_CHEERSTICK', 'IK3_KNUCKLEHAMMER', 'IK3_WAND', 'IK3_STAFF', 'IK3_YOYO', 'IK3_BOW', 'IK3_CROSSBOW', 'IK3_SHIELD', 'IK3_MAGICBARUNA', 'IK3_ZEMBARUNA', 'IK3_SHILDBARUNA'])  # rip flake or whatever tool i used to python code normalization lol


POS_WEAPON_NAME = 2
POS_IK3 = 7
POS_JOB = 8
POS_HANDED = 16
POS_DWPARAM = 53
POS_ADJPARAM = 53 + number_of_parameters
POS_SZICON = 133 - (6 - number_of_parameters) * 4

with open(path + "\\" + propItem_filename) as f:
    for line in f.readlines():
        line = line.strip()
        if line is None or line.startswith("//"):
            continue
    
        parameters_list = line.split("\t")
        
        if len(parameters_list) != 136 - (6 - number_of_parameters) * 4:
            continue
        
        weapon_type = parameters_list[POS_IK3]
        if weapon_type not in weapons_type:
            continue
        
        bonus = []
        
        for i in range(number_of_parameters):
            bonus_type = parameters_list[POS_DWPARAM + i]
            bonus_quantity = parameters_list[POS_ADJPARAM + i]
            
            if bonus_type == "=":
                continue
            
            bonus.append((bonus_type, bonus_quantity))
        
        weapons_type[weapon_type].append({
            'TXT_NAME': parameters_list[POS_WEAPON_NAME],
            'JOB': parameters_list[POS_JOB],
            'DOUBLE_HANDED': parameters_list[POS_HANDED] == 'HD_TWO',
            'ICON_IMAGE': parameters_list[POS_SZICON],
            'Bonus': bonus
        })
        
    
print(weapons_type)


