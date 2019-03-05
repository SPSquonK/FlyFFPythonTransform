
import re
from collections import OrderedDict
with open("NpcScript.cpp") as f:
    content = f.readlines()

result = OrderedDict()

lastNPC = ""
lastId = -1

def normalize(line):
    return line.strip().replace(chr(10), "").replace("\r", "")



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
            result[lastNPC].append({ 'ID': lastId, 'type': 'Speak', 'dial' : int(res.group(1)) })
        else:
            res = re.search('Say\(\s*([0-9]*)\s*\);', line)
            if res:
                result[lastNPC].append({ 'ID': lastId, 'type': 'Say', 'dial' : int(res.group(1)) })
        
    

s = []

for npcname, npc in result.items():
    for dic in npc:
        s.append(npcname + " " + str(dic['ID']) + " " + dic['type'] + " " + str(dic['dial']))
        
        
f = open("NpcOutput.txt", "w+")
for line in s:
    f.write(line + "\n")
f.close()



zawarudo = []

with open("WorldDialog.txt") as f:
    for line in f.readlines():
        zawarudo.append({'txt':normalize(line), 'used': False})


for npcname, npc in result.items():
    for dic in npc:
        if dic['dial'] < len(zawarudo):
            dic['dialtxt'] = zawarudo[dic['dial']]['txt']
            zawarudo[dic['dial']]['used'] = True
        else:
            dic['dialtxt'] = None



f = open("NpcOutputWithDial.txt", "w+")
for npcname, npc in result.items():
    for dic in npc:
        f.write(npcname + " " + str(dic['ID']) + " " + dic['type'] + " " + str(dic['dial']) + " " + str(dic['dialtxt']))
        f.write("\n")
f.close()


f = open("WorldDialogUnused.txt", "w+")
for line in zawarudo:
    if not line['used']:
        f.write(line['txt'])
        f.write("\n")
    
    
    
f.close()


