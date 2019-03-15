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


item_manager = items_manager.get_item_manager(number_of_parameters)
item_list = items_manager.get_item_list(path + propItem_filename)


# Read items to delete
items_to_remove = []


with open("items_to_remove.txt") as f:
    for line in f.readlines():
        line = line.strip()
        if line is None or len(line) == 0:
            continue
        
        m = re.findall(items_manager.ITEM_REGEX, line)
        
        if len(m) != 0:
            items_to_remove.append(m)


delete_items = []
rewritten_bonus = {}


        
for item_to_remove in items_to_remove:
    delete_items.append(item_to_remove[0])
    
    if len(item_to_remove) == 2:
        bonus = []
        
        bonus.extend(item_list[item_to_remove[1]]['Bonus'])
        bonus.extend(item_list[item_to_remove[0]]['Bonus'])
        rewritten_bonus[item_to_remove[1]] = bonus





new_propItemContent = []

with open(path + propItem_filename, encoding="ansi") as f:
    for line in f.readlines():    
        origline = line
        line = line.replace(str(chr(10)), "").replace("\r", "").strip()
        
        if line is None or line.startswith("//"):
            new_propItemContent.append(line)
            continue
        
        parameters_list = line.split("\t")
        
        if len(line) == 0:
            new_propItemContent.append("")
            continue
        
        if len(parameters_list) != item_manager['EXPECTED_LENGTH']:
            print("propItem is not well formed at line : " + line + " " + str(len(line)))
            exit(0)
            
        if parameters_list[item_manager['ID']] in delete_items:
            continue
            
        if parameters_list[item_manager['ID']] not in rewritten_bonus:
            new_propItemContent.append(line)
            continue
        
        id = parameters_list[item_manager['ID']]
        
        for i in range(min(len(rewritten_bonus[id]), item_manager['LEN_DW_PARAM'])):
            parameters_list[i + item_manager['START_DW_PARAM']] = rewritten_bonus[id][i][0]
            parameters_list[i + item_manager['START_ADJ_PARAM']] = rewritten_bonus[id][i][1]
        
        new_propItemContent.append("\t".join(parameters_list))


f = open("newPropItem.txt", "w+", encoding="ansi")
f.write("\n".join(new_propItemContent))
f.close()
