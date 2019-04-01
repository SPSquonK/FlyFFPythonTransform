#!/usr/bin/env python
import re
from collections import OrderedDict 
from jinja2 import Environment, FileSystemLoader
import argparse
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
        if isinstance(a, str):
            flat.append(a)
        else:
            for b in a:
                flat.append(b)

    return flat


def filter_item_with_ik3(item_list, flatten_item_kinds_3):
    new_item_list = OrderedDict()

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
    tooltips = OrderedDict()
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


def get_bonus_serialization(bonus_kind, bonus_value, bonus_types, bonus_types_rate):
    if bonus_kind in bonus_types:
        bonus_type_serialized = bonus_types[bonus_kind]
    else:
        bonus_type_serialized = bonus_kind
        bonus_types[bonus_kind] = bonus_kind

    percent_mark = "%" if bonus_kind in bonus_types_rate else ""

    return bonus_type_serialized + " + " + str(bonus_value) + percent_mark


def serialize_bonus_types(item_list, bonus_types, bonus_types_rate):
    def set_bonus_name(weapon):
        weapon['Bonus_Serialization'] = []

        for bonus_type, bonus_value in weapon['Bonus']:
            serial = get_bonus_serialization(bonus_type, bonus_value, bonus_types, bonus_types_rate)
            weapon['Bonus_Serialization'].append(serial)

    for item_id in item_list:
        set_bonus_name(item_list[item_id])


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


def serialize_items(item_list, job_list):
    def serialize_item(item):
        bonus_js = []
        bonus_js.extend(item['Bonus'])
        while len(bonus_js) != items_manager.nb_param():
            bonus_js.append(("=", 0))

        return {
            'icon': item['image_path'],
            'id': item['ID'],
            'IK3': item['IK3'],
            'DOUBLE_HANDED': item['DOUBLE_HANDED'],
            'JOB': item['JOB'],
            'OldLevel': item['OldLevel'],
            'Level': item['Level'],
            'name': item['WEAPON_NAME'],
            'WEAPON_NAME': item['WEAPON_NAME'],
            'job': job_list[item['JOB']]['Name'] if item['JOB'] in job_list else item['JOB'],
            'level': str(item['Level']) + job_list[item['JOB']]['ExtraSymbol'] if item['JOB'] in job_list else "",
            'bonus': '<br>'.join(item['Bonus_Serialization']),
            'bonuss': bonus_js
        }

    serialized_list = {}

    for item_id in item_list:
        serialized_list[item_id] = serialize_item(item_list[item_id])

    return serialized_list


def classify(serialization, item_kinds_3):
    def make_name(ik3):
        if isinstance(ik3, str):
            return ik3
        else:
            return "-".join(ik3)

    def is_valid(this_item, ik3):
        if isinstance(ik3, str):
            return this_item['IK3'] == ik3
        else:
            return this_item['IK3'] in ik3

    def item_comparator(w):
        return w['DOUBLE_HANDED'], items_manager.value_of_job(w['JOB']),\
            w['OldLevel'] if 'OldLevel' in w else w['Level'], w['WEAPON_NAME']

    classifications = []

    for i in range(len(item_kinds_3)):
        ik3_group = item_kinds_3[i]
        classification = {'Name': make_name(ik3_group), 'Items': []}

        for item_id in serialization:
            item = serialization[item_id]

            if is_valid(item, ik3_group):
                classification['Items'].append(item)

        classification['Items'] = sorted(classification['Items'], key=item_comparator)
        classifications.append(classification)

    return classifications


def write_page(j2_env, html_content, page_name='item_list.htm'):
    content = j2_env.get_template('general_template.htm').render(html_content=html_content)
    f = open(items_manager.THIS_DIR + page_name, "w+")
    f.write(content)
    f.close()


def fill_template(j2_env, template, classification, bonus_types):
    ik3 = classification['Name']
    weapons = classification['Items']

    title = ik3 + " " + str(len(weapons)) + " items"

    return j2_env.get_template(template).render(weaponname=title, weapons=weapons,
                                                bonustypes=bonus_types, nbparam=items_manager.nb_param())


def generate_html(j2_env, template_page, classified_serialization):
    html_code = []
    for i in range(len(classified_serialization)):
        html_code.append(fill_template(j2_env, template_page, classified_serialization[i], None))
    write_page(j2_env, "\r\n".join(html_code))


def generate_html_edit(j2_env, template_page, classified_serialization, bonus_types):
    for i in range(len(classified_serialization)):
        classification = classified_serialization[i]
        html_content = fill_template(j2_env, template_page, classification, bonus_types)
        write_page(j2_env, html_content, "item_list_" + classification['Name'] + ".htm")


def finish_processing_weapon(serialization, item_kinds_3, args_result, bonus_types, bonus_types_rate):
    classified_serialization = classify(serialization, item_kinds_3)

    # Page Generation
    j2_env = Environment(loader=FileSystemLoader(items_manager.THIS_DIR), trim_blocks=True)
    generate_html(j2_env, 'template.htm', classified_serialization)

    if args_result.edit:
        bonus_types_js = [{'DST': '=', 'Name': ''}]
        for bonus_type in bonus_types:
            percent = " (%)" if bonus_type in bonus_types_rate else ""
            bonus_types_js.append({'DST': bonus_type, 'Name': bonus_types[bonus_type] + percent})
        generate_html_edit(j2_env, 'template_js.htm', classified_serialization, bonus_types_js)


# ======================================================================================================================
# ======================================================================================================================
# -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS -- ARMORS

def group_armor_by_sex(serialization):
    def modify_id(original_id, letter):
        return original_id[0:position_char_to_replace] + letter + original_id[position_char_to_replace + 1:]

    constants = {'VALID_CHARACTER': "[0-9_A-Za-z]"}
    constants['REGEX_M'] = "II_ARM_M_" + constants['VALID_CHARACTER'] + "*"
    constants['REGEX_F'] = "II_ARM_F_" + constants['VALID_CHARACTER'] + "*"
    constants['REGEX_MEnd'] = "II_ARM_LC_" + constants['VALID_CHARACTER'] + "*" + "_M"
    constants['REGEX_FEnd'] = "II_ARM_LC_" + constants['VALID_CHARACTER'] + "*" + "_F"
    position_char_to_replace = 7

    grouped = {}
    used_items = set()

    for item_id in serialization:
        if item_id in used_items:
            continue

        if re.match(constants['REGEX_M'], item_id):
            corresponding_id = modify_id(item_id, 'F')
            is_male = True
        elif re.match(constants['REGEX_F'], item_id):
            corresponding_id = modify_id(item_id, 'M')
            is_male = False
        elif re.match(constants['REGEX_MEnd'], item_id):
            corresponding_id = item_id[:-1] + 'F'
            is_male = True
        elif re.match(constants['REGEX_FEnd'], item_id):
            corresponding_id = item_id[:-1] + 'M'
            is_male = False
        else:
            continue

        if corresponding_id in serialization:
            used_items.add(item_id)
            used_items.add(corresponding_id)

            if is_male:
                grouped[item_id] = (serialization[item_id], serialization[corresponding_id])
            else:
                grouped[corresponding_id] = (serialization[corresponding_id], serialization[item_id])

    for item_id in serialization:
        if item_id not in used_items:
            print(str(item_id) + " is excluded")

    return grouped

def group_armor_by_category(serialization):
    constants = {'VALID_CHARACTER': "[0-9_A-Za-z]"}
    # We don't group id that doesn't follow the REGEX_M scheme
    constants['REGEX_M'] = "II_ARM_M_" + constants['VALID_CHARACTER'] + "*"

    constants['START_REGEX'] = "II_ARM_M(_" + constants['VALID_CHARACTER'] + "*_?)?"
    constants['END_REGEX'] = "(_?" + constants['VALID_CHARACTER'] + "*)?"

    def match_with(item_id):
        possible_match = ['HELMET', 'SUIT', 'GAUNTLET', 'BOOTS']
        for part in possible_match:
            r = re.match(constants['START_REGEX'] + part + constants['END_REGEX'], item_id)
            if r is not None:
                return r.group(1), r.group(2), part

        return None

    grouped = {}
    solo = []

    for male_item_id in serialization:
        match_result = match_with(male_item_id)

        if match_result is None:
            solo.append(serialization[male_item_id])
        else:
            set_id = (match_result[0], match_result[1])
            if set_id not in grouped:
                grouped[set_id] = {}

            grouped[set_id][match_result[2]] = serialization[male_item_id]

    return grouped, solo

def read_raw_data_set():
    # It's basically a bad automat but I'm too lazy to find one or properly develop one
    # states = ['SetItem', '/*', 'SetItem{', 'ElemOrAvail', 'Elem{', 'InElem', 'Avail{', 'InAvail']
    d = {}
    state = 'SetItem'

    auto_next_state = {
        'SetItem{': 'ElemOrAvail',
        'Elem{': 'InElem',
        'Avail{': 'InAvail',
    }

    current_ids = ''

    with open(items_manager.path() + "propItemEtc.inc", encoding="utf-16-le") as f:
        for line in f.readlines():
            if state == 'SetItem':
                if line.startswith('/*'):
                    state = '/*'
                else:
                    m = re.findall("\\s*SetItem\\s*[0-9]*\\s*([A-Z0-9_a-z]*)(\\s*.*)?", line)
                    if m is not None and len(m) > 0:
                        current_ids = m[0][0]
                        d[current_ids] = {'parts': [], 'bonus': []}
                        state = 'SetItem{'
            elif state == '/*':
                if line.find('*/') != -1:
                    state = 'SetItem'
            elif state == 'ElemOrAvail':
                if line.find('Elem') != -1:
                    state = 'Elem{'
                elif line.find('Avail') != -1:
                    state = 'Avail{'
                elif line.find('}') != -1:
                    state = 'SetItem'
                else:
                    print("LINE = [" + line + "]")
                    raise Exception('Unexpected line in state ' + state)
            elif state == 'InElem':
                if line.find('}') != -1:
                    state = 'ElemOrAvail'
                else:
                    r = '[A-Za-z_0-9]+'
                    m = re.findall(r, line)

                    if m is not None and len(m) > 0:
                        d[current_ids]['parts'].append(m[0])
            elif state == 'InAvail':
                if line.find('}') != -1:
                    state = 'ElemOrAvail'
                else:
                    regex = '([A-Za-z_0-9]*)\\s*([0-9]*)\\s*([0-9])'
                    result = re.findall(regex, line)

                    if result is not None and len(result) > 0:
                        d[current_ids]['bonus'].append((int(result[0][2]), result[0][0], result[0][1]))
            else:
                state = auto_next_state[state]

    return d


def write_set_name(raw_data):
    def replacement(identifier, value):
        if identifier in raw_data:
            raw_data[identifier]['Name'] = value

    items_manager.read_text_file(items_manager.path() + 'propItemEtc.txt.txt', replacement)


def serialize_bonus(raw_data, bonus_types, bonus_types_rate):
    for armor_set_ids in raw_data:
        armor_set = raw_data[armor_set_ids]
        armor_set['Bonus_Serialization'] = {2:[], 3:[], 4:[]}
        for bonus_group in armor_set['bonus']:
            if bonus_group[0] in (2, 3, 4):
                serial = get_bonus_serialization(bonus_group[1], bonus_group[2], bonus_types, bonus_types_rate)
                armor_set['Bonus_Serialization'][bonus_group[0]].append(serial)


def read_existing_sets(bonus_types, bonus_types_rate):
    raw_data = read_raw_data_set()
    write_set_name(raw_data)
    serialize_bonus(raw_data, bonus_types, bonus_types_rate)

    return raw_data


def match_group_and_sets(solo, grouped_items_by_category, existing_sets):
    matching = {}

    # Solo Items
    for i in range(len(solo)):
        matching['SoloItem' + str(i)] = {
            'Name': "",
            'Bonus': [],
            'Bonus_Serialized': [],
            'Groups': [solo[i]],
            'Solo': True
        }

    # Groups
    def flatten_item(item_arrangment):
        item_list_male = []
        item_list_female = []

        for key in item_arrangment:
            item_list_male.append(item_arrangment[key][0]['id'])
            item_list_female.append(item_arrangment[key][1]['id'])

        return item_list_male, item_list_female

    i = 0
    for group_key in grouped_items_by_category:
        components_m, components_f = flatten_item(grouped_items_by_category[group_key])

        is_ok = False
        for set_ids in existing_sets:
            existing_set = existing_sets[set_ids]
            if set(components_m).issubset(set(existing_set['parts'])):
                is_ok = True
                break

        if not is_ok:
            matching['GroupItem' + str(i)] = {
                'Name': "",
                'Bonus': [],
                'Bonus_Serialized': [],
                'Groups': [grouped_items_by_category[group_key]],
                'Solo': False
            }
            i = i + 1
        else:
            if set_ids not in matching:
                matching[set_ids] = {
                    'Name': existing_set['Name'],
                    'Bonus': existing_set['bonus'],
                    'Bonus_Serialized': existing_set['Bonus_Serialization'],
                    'Groups': [],
                    'Solo': False
                }

            matching[set_ids]['Groups'].append(grouped_items_by_category[group_key])

    return matching


def group_comparator(g):
    return g['level'], g['job'], g['name']


def extract_one_item(set_groups):
    first_group = set_groups['Groups'][0]

    if set_groups['Solo']:
        return first_group[0]
    else:
        for item_group in first_group.values():
            return item_group[0]
        return None


def normalize_subgroups(group):
    subgroups = []
    for subgroup in group['Groups']:
        if group['Solo']:
            subgroups.append([{
                'male_icon': subgroup[0]['icon'],
                'female_icon': subgroup[1]['icon'],
                'male_name': subgroup[0]['name'],
                'female_name': subgroup[1]['name'],
                'bonus': subgroup[0]['bonus'],
            }])
        else:
            l = []

            for part_name in subgroup:
                part_item = subgroup[part_name]
                l.append({
                    'male_icon': part_item[0]['icon'],
                    'female_icon': part_item[1]['icon'],
                    'male_name': part_item[0]['name'],
                    'female_name': part_item[1]['name'],
                    'bonus': part_item[0]['bonus'],
                })

            subgroups.append(l)

    return subgroups


def normalize_armors(set_groups):
    global_d = []

    for group_id in set_groups:
        group = set_groups[group_id]
        one_item = extract_one_item(group)
        global_d.append({
            'name': group['Name'],
            'level': one_item['Level'],
            'job': one_item['job'],
            'bonus': group['Bonus_Serialized'],  # bonuss
            'subgroups': normalize_subgroups(group)
        })

    return sorted(global_d, key=group_comparator)


def finish_processing_armors(serialization, item_kinds_3, args_result, bonus_types, bonus_types_rate):
    # Existing sets
    existing_sets = read_existing_sets(bonus_types, bonus_types_rate)

    # Reading items
    grouped_items_by_sex = group_armor_by_sex(serialization)
    grouped_items_by_category, solo = group_armor_by_category(grouped_items_by_sex)

    # Matching groups with sets
    set_groups = match_group_and_sets(solo, grouped_items_by_category, existing_sets)

    j2_env = Environment(loader=FileSystemLoader(items_manager.THIS_DIR), trim_blocks=True)
    normalized_armors = normalize_armors(set_groups)

    code = j2_env.get_template('template_armors.htm').render(groups=normalized_armors, bonus_types=bonus_types)
    f = open(items_manager.THIS_DIR + "armor_list.html", "w+")
    f.write(code)
    f.close()


# ======================================================================================================================
# ======================================================================================================================
# -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN  -- MAIN


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
                                 lambda identifier, txt: replace_txt(item_list, identifier, txt))

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
    serialization = serialize_items(item_list, job_list)

    if args_result.kind == 'weapons':
        finish_processing_weapon(serialization, item_kinds_3, args_result, bonus_types, bonus_types_rate)
    elif args_result.kind == 'armors':
        finish_processing_armors(serialization, item_kinds_3, args_result, bonus_types, bonus_types_rate)


if __name__ == '__main__':
    main()
