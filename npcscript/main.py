
import re
from collections import OrderedDict
with open("NpcScript.cpp") as f:
    content = f.readlines()

result = OrderedDict()

lastNPC = ""
lastId = -1



for line in content:
    res = re.search('void CNpcScript::(.*)_([0-9]*)\\(\\)', line)
    
    if res:
        lastNPC = str(res.group(1))
        lastId = int(res.group(2))
        if not result.has_key(lastNPC):
            result[lastNPC] = []
            
    else:
        res = re.search('Speak\(\s*NpcId\(\)\s*,\s*([0-9]*)\s*\);', line)
        
        if res:
            result[lastNPC].append({ 'ID': lastId, 'type': 'Speak', 'dial' : res.group(1) })
        else:
            res = re.search('Say\(\s*([0-9]*)\s*\);', line)
            if res:
                result[lastNPC].append({ 'ID': lastId, 'type': 'Say', 'dial' : res.group(1) })
        
    

s = []


for npcname, npc in result.items():
    for dic in npc:
        s.append(npcname + " " + str(dic['ID']) + " " + dic['type'] + " " + str(dic['dial']))
        
        



f = open("NpcOuput.txt", "w+")
for line in s:
    f.write(line + "\n")
f.close()