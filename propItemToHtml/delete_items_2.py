import sys
import re
import string
from collections import OrderedDict 
from jinja2 import Environment, FileSystemLoader
import os

path = "..\\..\\FlyFF-VS17\\Resource\\" if len(sys.argv) < 2 else sys.argv[1]
propItem_filename = "propItem.txt" if len(sys.argv) < 3 else sys.argv[2]




ids = []

with open("items_to_delete.csv", encoding="iso-8859-1") as f:
    for line in f.readlines():
        if not line.startswith("x"):
            continue
        
        ids.append(line[line.find("\t") + 1:line.find("\t", 2)])


content = []

with open(path + propItem_filename, encoding="ansi") as f:
    for line in f.readlines():
        m = re.findall("[0-9]*\s*([A-Za-z0-9_]*)\s*", line)
        
        if m is None or len(m) == 0 or m[0].strip() is None or m[0].strip() == "" or  m[0] not in ids:
            content.append(line)
        
        







f = open("newPropItem.txt", "w+", encoding="ansi")
f.write("".join(content))
f.close()
