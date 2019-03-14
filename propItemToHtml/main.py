import sys
import re
import string
from collections import OrderedDict 
from jinja2 import Environment, FileSystemLoader
import os

path = "..\\..\\FlyFF-VS17\\Resource\\" if len(sys.argv) < 2 else sys.argv[1]
propItem_filename = "propItem.txt" if len(sys.argv) < 3 else sys.argv[2]
number_of_parameters = 6 if len(sys.argv) < 4 else sys.argv[3]

weapons_type = OrderedDict()


def for_each_weapon(used_function):
    for weapon_type in weapons_type:
        for weapon in weapons_type[weapon_type]:
            used_function(weapon)


def add_types(dict, list):
    for item in list:
        dict[item] = []


add_types(weapons_type, ['IK3_SWORD', 'IK3_AXE', 'IK3_CHEERSTICK', 'IK3_KNUCKLEHAMMER', 'IK3_WAND', 'IK3_STAFF', 'IK3_YOYO', 'IK3_BOW', 'IK3_CROSSBOW', 'IK3_SHIELD', 'IK3_MAGICBARUNA', 'IK3_ZEMBARUNA', 'IK3_SHILDBARUNA'])  # rip flake or whatever tool i used for python code normalization lol


POS_WEAPON_NAME = 2
POS_IK3 = 7
POS_JOB = 8
POS_HANDED = 16
POS_DWPARAM = 53
POS_ADJPARAM = 53 + number_of_parameters
POS_SZICON = 132 - (6 - number_of_parameters) * 4

if path[-1] != '\\':
    path = path + '\\'


with open(path + propItem_filename, encoding="ansi") as f:
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
            'ICON_IMAGE': parameters_list[POS_SZICON].replace("\"", ""),
            'Level': 1,
            'Bonus': bonus
        })
        

# Convert IDS Name to real names

def read_text_file(file, replacement_function ,encoding="utf-16-le"):
    with open(file, encoding=encoding) as f:
        for line in f.readlines():
            line.replace(chr(10), " ")
            index = line.find(" ")
            indextab = line.find("\t")
            
            if index == -1 and indextab == -1:
                continue
            
            if indextab != -1:
                if index == -1:
                    index = indextab
                else:
                    index = min(index, indextab)
            
            identifier = line[0:index]
            text = line[index:].strip()
            
            if text is None:
                continue
            
            replacement_function(identifier, text)

def replace_txt(identifier, text):
    for weapon_type in weapons_type:
        for weapon in weapons_type[weapon_type]:
            if weapon['TXT_NAME'] == identifier:
                weapon['WEAPON_NAME'] = text

read_text_file(path + "propItem.txt.txt", replace_txt)

# Detect tid_tooltip name
tooltips = {}
mode = 0
with open(path + "textClient.inc", encoding="utf-16-le") as f:
    for line in f.readlines():
        if mode == 0:
            if line.startswith("TID_TOOLTIP_"):
                space_pos = line.find("0x")
                tooltip = line[len("TID_TOOLTIP_"):space_pos].strip()
                mode = 1
        elif mode == 1:
            mode = 2
        else:
            tooltips[tooltip] = line.strip()
            mode = 0
    
    
def replace_tooltip(identifier, text):
    for tooltip_name in tooltips:
        if tooltips[tooltip_name] == identifier:
            tooltips[tooltip_name] = text
            
read_text_file(path + "textClient.txt.txt", replace_tooltip)


def set_bonus_name(weapon):
    weapon['Bonus_Serialization'] = []
    
    for bonus_type, bonus_value in weapon['Bonus']:
        if bonus_type in tooltips:
            bonus_type_serialized = tooltips[bonus_type]
        elif "DST_" + bonus_type in tooltips:
            bonus_type_serialized = tooltips["DST_" + bonus_type]
        else:
            bonus_type_serialized = bonus_type
        
        weapon['Bonus_Serialization'].append(bonus_type_serialized + " + " + str(bonus_value))
    
    

for_each_weapon(set_bonus_name)


# Convert icons

#from PIL import Image

def compute_icon(weapon):
    if weapon['ICON_IMAGE'] is None:
        weapon['image_path'] = ""
        return
    
    img = "Item\\" + weapon['ICON_IMAGE'][:-3] + "png"
    weapon['image_path'] = img

    
    
    
    
    


for_each_weapon(compute_icon)


# Generate HTML
def serialize(weapon_type):
    dict = []
    
    for w in weapon_type:
        dict.append({
            'icon': w['image_path'],
            'name': w['WEAPON_NAME'],
            'job': w['JOB'],
            'level': w['Level'],
            'bonus': '<br>'.join(w['Bonus_Serialization'])
        })
        
    return dict
    


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


html_file = ""


j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

template = j2_env.get_template('template.htm')




with open("template_begin.htm") as f:
    for line in f.readlines():
        html_file += "\r\n" + line


for weapon_type in weapons_type:
    html_file += "\r\n" + template.render(weaponname=weapon_type, weapons=serialize(weapons_type[weapon_type]))


with open("template_end.htm") as f:
    for line in f.readlines():
        html_file += "\r\n" + line



f = open("itemlist.html", "w+")
f.write(html_file)
f.close()
