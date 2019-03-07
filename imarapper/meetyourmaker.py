import re

## Load ITEM
items = []
with open("weaponsid.txt") as f:
    for line in f.readlines():
        items.append(line.replace(chr(10), "").replace("\r", "").lower())


foundyoyomodel = {}

# Determine which sfx we need
with open("mdlDyna.inc") as f:
    for m in f.readlines():
        regex_search = re.search("\"([a-zA-Z_]*)\"\\s*([a-zA-Z_]*)\\s*.*", m)
        
        if not regex_search:
            continue
        model = regex_search.group(1).lower()
        identifier = regex_search.group(2).lower()
        
        if identifier in items:
            foundyoyomodel[model] = False


with open("mdlDyna.inc") as f:
    for m in f.readlines():
        regex_search = re.search("\"([a-zA-Z_]*)\"\\s*([a-zA-Z_]*)\\s*.*", m)
        
        if not regex_search:
            continue
        model = regex_search.group(1).lower()
        identifier = regex_search.group(2).lower()
        
        if identifier.startswith("xi_item_"):
            if model[0:4] == 'sfx_' and foundyoyomodel.has_key(model[4:]):
                foundyoyomodel[model[4:]] = True


for k, v in foundyoyomodel.items():
    if not v:
        print(k)

'''

## SFX FILE MODEL
# Load sfx, get static part of yoyo sfx
f1 = []
filename1 = "sfx_weayoycisica.sfx"

with open(filename1) as f:
  while True:
    c = f.read(1)
    if not c:
      break
    f1.append(c)


model_name = "item_weayoycisica.o3d"
index = ''.join(f1).find(model_name)
index_size = index - 4
start = f1[0:index_size]
end = f1[index + len(model_name):]


madesfx = []

for m in mdl:
    makesfx = False
    for item in sitems:
        weaponmodel = re.search("\"([a-zA-Z]*)\"\\s*" + item + "\s*", m)
        if not weaponmodel:
            continue
        
            
        weaponmodel = weaponmodel.group(1)
        madesfx.append("XI_AUTOYOYO_" + weaponmodel)
        weaponmodeln = "item_" + weaponmodel + ".o3d"
        
        
        bytes = []
        bytes.extend(start)
        bytes.append(chr(len(weaponmodeln)))
        bytes.append(chr(0))
        bytes.append(chr(0))
        bytes.append(chr(0))
        bytes.extend(weaponmodeln)
        bytes.extend(end)
        
        sfxfile = "sfx_a" + weaponmodel + ".sfx"
        
        with open(sfxfile, "wb") as file:
            file.write(bytearray(bytes))
  

       
        
        break



'''
