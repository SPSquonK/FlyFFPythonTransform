#!/usr/bin/env python
import sys
import re
from collections import OrderedDict 
from jinja2 import Environment, FileSystemLoader
import argparse
import collections
# Custom import
import items_manager


# Gives the list of IK3 to retrieve according to the given kind
def get_categorization_from_kind(kind):
    if kind == 'weapons':
        return ['IK3_SWD', 'IK3_AXE', 'IK3_CHEERSTICK', 'IK3_KNUCKLEHAMMER', 'IK3_WAND', 'IK3_STAFF', 'IK3_YOYO',
                'IK3_BOW', 'IK3_CROSSBOW', 'IK3_SHIELD', 'IK3_MAGICBARUNA', 'IK3_ZEMBARUNA']
    elif kind == 'armors':
        return [['IK3_HELMET', 'IK3_SUIT', 'IK3_GAUNTLET', 'IK3_BOOTS']]
    else:
        raise Exception('Unexpected kind ' + kind)


def make_list_from_categorization(categorization):
    flat = []

    for a in categorization:
        if isinstance(a, collections.Iterable):
            for b in a:
                flat.append(b)
        else:
            flat.append(a)

    return flat


def filter_item_with_ik3(item_list, flatten_item_kinds_3):
    new_item_list = {}

    for item in item_list:
        if item_list[item]['IK3'] in flatten_item_kinds_3:
            new_item_list[item] = item_list[item]

    return new_item_list


def make_arg_parser():
    arg_parser = argparse.ArgumentParser(description="Creates a html page with every weapons or armors in the game")

    arg_parser.add_argument('-e', '--edit', action='store_true',
                            help='Generates several html page with edit options that generates '
                            'the content of a file that the modify_bonus.py script can use to alter the source files.')
    arg_parser.add_argument('-k', '--kind', choices=['weapons', 'armors'], default='weapons',
                            help='Defines the kind of items that will be displayed')

    return arg_parser


# Replace IDS name with real name
def replace_txt(item_list, identifier, text):
    for weapon_id in item_list:
        if item_list[weapon_id]['TXT_NAME'] == identifier:
            item_list[weapon_id]['WEAPON_NAME'] = text


def read_bonus_types():
    tooltips = {}
    tooltips_rate = {}

    # Read WndManager to read existing bonus
    mode = 0  # 0 = search for an array, 1 = tooltip, 2 = rate
    with open(items_manager.path() + "..\\Source\\_Interface\\WndManager.cpp", encoding="cp949") as f:
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
                    if mode == 1:  # Read dst types
                        m = re.findall("(DST_[A-Z_]*)\\s*,\\s*([A-Z_]*)", line)

                        if m is not None and len(m) != 0:
                            tooltips[m[0][0]] = m[0][1]

                    else:  # Read rates kind
                        m = re.findall("(DST_[A-Z_]*)", line)
                        if m is not None and len(m) != 0:
                            tooltips_rate[m[0]] = True

    # Search corresponding IDS with define
    mode = 0
    with open(items_manager.path() + "textClient.inc", encoding="utf-16-le") as f:
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

    # Convert IDS to text
    def replace_tooltip(identifier, text):
        for tooltip_name in tooltips:
            if tooltips[tooltip_name] == identifier:
                tooltips[tooltip_name] = text

    items_manager.read_text_file(items_manager.path() + "textClient.txt.txt", replace_tooltip)

    return tooltips, tooltips_rate


def serialize_bonus_types(item_list, bonus_types, bonus_types_rate):
    def set_bonus_name(weapon):
        weapon['Bonus_Serialization'] = []

        for bonus_type, bonus_value in weapon['Bonus']:
            if bonus_type in bonus_types:
                bonus_type_serialized = bonus_types[bonus_type]
            else:
                bonus_type_serialized = bonus_type
                bonus_types[bonus_type] = bonus_type

            percent_mark = "%" if bonus_type in bonus_types_rate else ""

            weapon['Bonus_Serialization'].append(bonus_type_serialized + " + " + str(bonus_value) + percent_mark)

    for item_id in item_list:
        set_bonus_name(item_list[item_id])

    return 0


def read_jobs():
    # Read jobs names
    job_names = {}

    def define_job_names(identifier, value):
        # Removes extra chracters before IDS
        if not identifier.startswith("IDS"):
            identifier = identifier[identifier.find("IDS"):]

        job_names[identifier] = value

    items_manager.read_text_file(items_manager.path() + "etc.txt.txt", define_job_names, "utf-16-le")

    # Build jobs properties
    jtype_with_symbols = {'JTYPE_MASTER': "-M", 'JTYPE_HERO': "-H"}

    jobs = {}

    with open(items_manager.path() + "etc.inc", encoding="utf-16-le") as f:
        for line in f.readlines():
            line = line.strip()
            m = re.findall("(JOB_[A-Z_]*)\\s*(IDS_ETC_[A-Z_0-9]*)\\s*[A-Z_0-9]*\\s*(JTYPE_[A-Z]*)", line)

            if m is None or len(m) == 0:
                continue

            m = m[0]

            jobs[m[0]] = {
                'Name': job_names[m[1]],
                'ExtraSymbol': '' if m[2] not in jtype_with_symbols else jtype_with_symbols[m[2]]
            }

    return jobs


# Builds image_path field in every item
def compute_icons(item_list):
    for item_id in item_list:
        weapon = item_list[item_id]

        if weapon['ICON_IMAGE'] is None:
            weapon['image_path'] = ""
            return

        img = "Item\\" + weapon['ICON_IMAGE'][:-3] + "png"
        weapon['image_path'] = img


def classify(a, b):
    return 0

def serialize_items(a, job_list, b):
    return 0

def main():
    arg_parser = make_arg_parser()
    args_result = arg_parser.parse_args()

    # Read propItem
    item_list = items_manager.get_item_list()

    # Read categories
    item_kinds_3 = get_categorization_from_kind(args_result.kind)
    flatten_item_kinds_3 = make_list_from_categorization(item_kinds_3)

    # Filter items
    item_list = filter_item_with_ik3(item_list, flatten_item_kinds_3)

    # Replace item names
    items_manager.read_text_file(items_manager.path() + "propItem.txt.txt",
                                 lambda id, txt: replace_txt(item_list, id, txt))

    # Serialize bonus types
    bonus_types, bonus_types_rate = read_bonus_types()
    serialize_bonus_types(item_list, bonus_types, bonus_types_rate)

    # Icons
    compute_icons(item_list)

    # Legendary Emerald Volcano Terra Sun Zero Project
    if items_manager.adjustForLEVTSZF():
        items_manager.adjust_for_levtszf(item_list)

    # Categorization
    job_list = read_jobs()
    serialization = serialize_items(item_list, job_list, args_result.edit)

    classified_serialization = classify(serialization, item_kinds_3)


    '''
    for i in item_list:
        print(item_list[i]['WEAPON_NAME'])
    '''


if __name__ == '__main__':
    main()

exit(0)

js = len(sys.argv) >= 2 and sys.argv[1] == "JS"

weapons_type = OrderedDict()

def for_each_weapon(used_function):
    for weapon_type in weapons_type:
        for weapon in weapons_type[weapon_type]:
            used_function(weapon)


# Generate HTML





def append_one_weapon(dict, w):
    bonuss = []
    bonuss.extend(w['Bonus'])
    while len(bonuss) != items_manager.nb_param():
        bonuss.append(("=", 0))

    dict.append({
        'icon': w['image_path'],
        'id': w['ID'],
        'name': w['WEAPON_NAME'],
        'job': jobs[w['JOB']]['Name'] if w['JOB'] in jobs else w['JOB'],
        'level': str(w['Level']) + jobs[w['JOB']]['ExtraSymbol'] if w['JOB'] in jobs else "",
        'bonus': '<br>'.join(w['Bonus_Serialization']),
        'bonuss': bonuss
    })


def serialize_js(weapon_type):
    def weapon_comparator(w):
        return w['DOUBLE_HANDED'], items_manager.value_of_job(w['JOB']),\
               w['OldLevel'] if 'OldLevel' in w else w['Level'], w['WEAPON_NAME']

    d = []

    weapons = sorted(weapon_type, key=weapon_comparator)

    for w in weapons:
        append_one_weapon(d, w)
        
    return d


bonustypes = []

if js:
    serialize = serialize_js
    
    bonustypes.append({ 'DST': '=', 'Name': '' })
    for t in tooltips:
        percent = " (%)" if t in tooltips_rate else ""
    
        bonustypes.append({'DST': t, 'Name': tooltips[t] + percent})
    
    template = 'template_js.htm'
else:
    serialize = serialize_js
    template = 'template.htm'



html_file = ""

j2_env = Environment(loader=FileSystemLoader(items_manager.THIS_DIR), trim_blocks=True)

ijustwanttobreaktherules = ""

def generate_templated_page(weapon_type, template_page):
    weapon_dscr = weapon_type + " " + str(len(weapons_type[weapon_type])) + " weapons"

    return "\r\n" + j2_env.get_template(template).render(weaponname=weapon_dscr, weapons=serialize(weapons_type[weapon_type]), bonustypes=bonustypes, nbparam=items_manager.nb_param())


def generate_general_page(ijustwanttobreaktherules, page_name="itemlist.html"):
    content = j2_env.get_template('general_template.htm').render(idontwannagotoschool=ijustwanttobreaktherules)
    f = open(items_manager.THIS_DIR + page_name, "w+")
    f.write(content)
    f.close()

if js:
    for weapon_type in weapons_type:
        ijustwanttobreaktherules = generate_templated_page(weapon_type, template)
        generate_general_page(ijustwanttobreaktherules, "item_list_" + weapon_type + ".htm")
else:
    ijustwanttobreaktherules = ""
    for weapon_type in weapons_type:
        ijustwanttobreaktherules += generate_templated_page(weapon_type, template)
    generate_general_page(ijustwanttobreaktherules)



