import sys
import re
import string
from collections import OrderedDict 
from jinja2 import Environment, FileSystemLoader
import os

import items_manager

path = "..\\..\\FlyFF-VS17\\Resource\\" if len(sys.argv) < 2 else sys.argv[1]
propItem_filename = "propItem.txt" if len(sys.argv) < 3 else sys.argv[2]
number_of_parameters = 6 if len(sys.argv) < 4 else sys.argv[3]

weapons_type = OrderedDict()

def for_each_weapon(used_function):
    for weapon_type in weapons_type:
        for weapon in weapons_type[weapon_type]:
            used_function(weapon)


# Function to read .txt.txt files
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
            
def add_types(dict, list):
    for item in list:
        dict[item] = []


add_types(weapons_type, ['IK3_SWD', 'IK3_AXE', 'IK3_CHEERSTICK', 'IK3_KNUCKLEHAMMER', 'IK3_WAND', 'IK3_STAFF',
                         'IK3_YOYO', 'IK3_BOW', 'IK3_CROSSBOW', 'IK3_SHIELD', 'IK3_MAGICBARUNA', 'IK3_ZEMBARUNA'])

# Normalize path
if path[-1] != '\\':
    path = path + '\\'

# Read propItem
item_list = items_manager.get_item_list(path + propItem_filename)

for item_name in item_list:
    item = item_list[item_name]
    ik3 = item['IK3']
    
    if ik3 in weapons_type:
        weapons_type[ik3].append(item)


# Replace IDS name with real name
def replace_txt(identifier, text):
    for weapon_type in weapons_type:
        for weapon in weapons_type[weapon_type]:
            if weapon['TXT_NAME'] == identifier:
                weapon['WEAPON_NAME'] = text

read_text_file(path + "propItem.txt.txt", replace_txt)


# Look for tooltip corresponding to dst
tooltips = {}
tooltips_rate = {}

with open(path + "..\\Source\\_Interface\\WndManager.cpp", encoding="cp949") as f:
    mode = 0  # 0 = search for an array, 1 = tooltip, 2 = rate
    for line in f.readlines():
        line = line.strip().replace(u"\ufeff", "")
        if mode == 0:
            if line.startswith("static DST_STRING g_DstString[] ="):
                mode = 1
            elif line.startswith("static constexpr int nDstRate[] = {"):
                mode = 2
        else:
            if line == "};":
                mode = 0
            else:
                if mode == 1:
                
                    m = re.findall("(DST_[A-Z_]*)\s*,\s*([A-Z_]*)", line)
                    
                    if m is not None and len(m) != 0:
                        tooltips[m[0][0]] = m[0][1]
                
                else :
                    m = re.findall("(DST_[A-Z_]*)", line)
                    if m is not None and len(m) != 0:
                        tooltips_rate[m[0]] = True

mode = 0
with open(path + "textClient.inc", encoding="utf-16-le") as f:
    for line in f.readlines():
        if mode == 0:
            space_pos = line.find("0x")
            tooltip = line[:space_pos].strip()
            
            for t in tooltips:
                if tooltips[t] == tooltip:
                    tooltip_id = t
                    mode = 1
                    break
            
        elif mode == 1:
            mode = 2
        else:
            tooltips[tooltip_id] = line.strip()
            mode = 0
    
    
def replace_tooltip(identifier, text):
    for tooltip_name in tooltips:
        if tooltips[tooltip_name] == identifier:
            tooltips[tooltip_name] = text


read_text_file(path + "textClient.txt.txt", replace_tooltip)

# Set jobs names
job_names = {}
def define_job_names(ident, value):
    if not ident.startswith("IDS"):
        ident = ident[ident.find("IDS"):]

    job_names[ident] = value

read_text_file(path + "etc.txt.txt", define_job_names, "utf-16-le")


jtype_with_symbols = {'JTYPE_MASTER' : "-M", 'JTYPE_HERO' : "-H"}

jobs = {}

with open(path + "etc.inc", encoding="utf-16-le") as f:
    for line in f.readlines():
        line = line.strip()
        m = re.findall("(JOB_[A-Z_]*)\s*(IDS_ETC_[A-Z_0-9]*)\s*[A-Z_0-9]*\s*(JTYPE_[A-Z]*)", line)

        if m is None or len(m) == 0:
            continue

        m = m[0]

        jobs[m[0]] = {
            'Name': job_names[m[1]],
            'ExtraSymbol': '' if m[2] not in jtype_with_symbols else jtype_with_symbols[m[2]]
        }

def set_bonus_name(weapon):
    weapon['Bonus_Serialization'] = []
    
    for bonus_type, bonus_value in weapon['Bonus']:
        if bonus_type in tooltips:
            bonus_type_serialized = tooltips[bonus_type]
        else:
            bonus_type_serialized = bonus_type

        percent_mark = "%" if bonus_type in tooltips_rate else ""

        weapon['Bonus_Serialization'].append(bonus_type_serialized + " + " + str(bonus_value) + percent_mark)
    

for_each_weapon(set_bonus_name)

# Convert icons to png file that the user has converted itself because python can't do it :>
def compute_icon(weapon):
    if weapon['ICON_IMAGE'] is None:
        weapon['image_path'] = ""
        return
    
    img = "Item\\" + weapon['ICON_IMAGE'][:-3] + "png"
    weapon['image_path'] = img


for_each_weapon(compute_icon)


# Generate HTML

jobs_values = [
    ['JOB_VAGRANT', 'JOB_MERCENARY', 'JOB_ACROBAT', 'JOB_ASSIST', 'JOB_MAGICIAN',
     'JOB_KNIGHT', 'JOB_BLADE', 'JOB_JESTER', 'JOB_RANGER',
     'JOB_RINGMASTER', 'JOB_BILLPOSTER', 'JOB_PSYCHIKEEPER', 'JOB_ELEMENTOR'],
    ['JOB_KNIGHT_MASTER', 'JOB_BLADE_MASTER', 'JOB_JESTER_MASTER', 'JOB_RANGER_MASTER',
     'JOB_RINGMASTER_MASTER', 'JOB_BILLPOSTER_MASTER', 'JOB_PSYCHIKEEPER_MASTER', 'JOB_ELEMENTOR_MASTER'],
    ['JOB_KNIGHT_HERO', 'JOB_BLADE_HERO', 'JOB_JESTER_HERO', 'JOB_RANGER_HERO',
     'JOB_RINGMASTER_HERO', 'JOB_BILLPOSTER_HERO', 'JOB_PSYCHIKEEPER_HERO', 'JOB_ELEMENTOR_HERO'],
    ['JOB_LORDTEMPLER_HERO', 'JOB_STORMBLADE_HERO', 'JOB_WINDLURKER_HERO', 'JOB_CRACKSHOOTER_HERO',
     'JOB_FLORIST_HERO', 'JOB_FORCEMASTER_HERO', 'JOB_MENTALIST_HERO', 'JOB_ELEMENTORLORD_HERO'],
    ['JOB_HERO']
]

def value_of_job(job_name):

    for i in range(len(jobs_values)):
        if job_name in jobs_values[i]:
            return i

    return -1


def weapon_comparator(w):
    return (w['DOUBLE_HANDED'], value_of_job(w['JOB']), w['OldLevel'], w['WEAPON_NAME'])

def legendary_emerald_volcano_terra_sun_zero_flyff_adjustements(w):
    if w['JOB'].find("_MASTER") != -1 or w['JOB'].find("_HERO") != -1:
        for list in jobs_values:
            if w['JOB'] not in list:
                continue

            index = list.index(w['JOB'])
            w['JOB'] = jobs_values[0][index + 5]
            break
    w['OldLevel'] = w['Level']
    
    if w['Level'] <= 15:
        w['Level'] = 1
    elif w['Level'] < 60:
        w['Level'] = int((w['Level'] - 15) / 3 + 5)
    elif w['Level'] <= 125:
        w['Level'] = w['Level'] - 40
    else:
        w['Level'] = 100

for_each_weapon(legendary_emerald_volcano_terra_sun_zero_flyff_adjustements)

def serialize(weapon_type):
    dict = []
    
    weapons = sorted(weapon_type, key=weapon_comparator)
    
    for w in weapons:
        dict.append({
            'icon': w['image_path'],
            'id': w['ID'],
            'name': w['WEAPON_NAME'],
            'job': jobs[w['JOB']]['Name'] if w['JOB'] in jobs else w['JOB'],
            'level': str(w['Level']) + jobs[w['JOB']]['ExtraSymbol'] if w['JOB'] in jobs else "",
            'bonus': '<br>'.join(w['Bonus_Serialization'])
        })
        
    return dict
    


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


html_file = ""


j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

ijustwanttobreaktherules = ""
for weapon_type in weapons_type:
    weapon_dscr = weapon_type + " " + str(len(weapons_type[weapon_type])) + " weapons"

    ijustwanttobreaktherules += "\r\n"\
                                + j2_env.get_template('template.htm')\
                                        .render(weaponname=weapon_dscr, weapons=serialize(weapons_type[weapon_type]))

content = j2_env.get_template('general_template.htm').render(idontwannagotoschool=ijustwanttobreaktherules)


if True:
    f = open("items.csv", "w+")
    
    def weapon_comparator2(w):
        return (w['OldLevel'], list(w['WEAPON_NAME']).reverse())
    
    sss = []
    for t in weapons_type:
        for w in weapons_type[t]:
            sss.append(w)
    
    
    for w in sorted(sss, key=weapon_comparator2):
        f.write("\t".join([w['ID'], w['WEAPON_NAME'], str(w['Level']), str(w['OldLevel']), w['JOB'], ';'.join(w['Bonus_Serialization'])]) + "\n")
    
    f.close()
    
    
    


f = open("itemlist.html", "w+")
f.write(content)
f.close()
