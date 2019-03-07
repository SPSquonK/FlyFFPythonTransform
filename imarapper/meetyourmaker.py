import re

## Load ITEM
items = []
with open("propItem.txt") as f:
    for line in f.readlines():
        is_yoyo = line.find("IK3_YOYO")
        
        if is_yoyo == -1:
            continue
        
        items.append(re.search("[0-9]*\\s*([a-zA-Z_0-9]*)\\s*", line).group(1))

print(items)

foundyoyomodel = {}

# Determine which sfx we need
with open("mdlDyna.inc") as f:
    for m in f.readlines():
        regex_search = re.search("\"([a-zA-Z_0-9]*)\"\\s*([a-zA-Z_0-9]*)\\s*.*", m)
        
        if not regex_search:
            continue
        model = regex_search.group(1).lower()
        identifier = regex_search.group(2).lower()
        
        if identifier in items:
            if foundyoyomodel.has_key(model):
                foundyoyomodel[model]['items'].append(identifier)
            else:
                foundyoyomodel[model] = { 'checked' : False, 'items' : [identifier] }
            


with open("mdlDyna.inc") as f:
    for m in f.readlines():
        regex_search = re.search("\"([a-zA-Z_0-9]*)\"\\s*([a-zA-Z_0-9]*)\\s*.*", m)
        
        if not regex_search:
            continue
        model = regex_search.group(1).lower()
        identifier = regex_search.group(2).lower()
        
        if identifier.startswith("xi_item_"):
            if model[0:4] == 'sfx_' and foundyoyomodel.has_key(model[4:]):
                foundyoyomodel[model[4:]]['checked'] = True


for k, v in foundyoyomodel.items():
    if not v['checked']:
        print("Item_" + k + ".o3d" + "       " + k + "        " + "sfx_" + k)

print
print

for k, v in foundyoyomodel.items():
    if not v['checked']:
        print("\t\"sfx_" + k + "\"\t XI_ITEM_YOYO_ATK" + k[6:].upper() + "\tMODELTYPE_SFX \"\" 0  MD_NEAR 0  1.0f 0 1 ATEX_NONE 1")

print
print

for k, v in foundyoyomodel.items():
    if not v['checked']:
        print("#define XI_ITEM_YOYO_ATK" + k[6:].upper() + " 0")


print
print

for k, v in foundyoyomodel.items():
    if not v['checked']:
        for i in v['items']:
            print(i.upper() + " -> XI_ITEM_YOYO_ATK" + k[6:].upper())


'''
"sfx_weayoyaquabr"	    XI_ITEM_YOYO_ATK15			MODELTYPE_SFX "" 0  MD_NEAR 0  1.0f 0 1 ATEX_NONE 1

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
