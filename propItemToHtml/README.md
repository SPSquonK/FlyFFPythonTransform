# propItem to HTML

## Goal

### main.py

Generate a nice html file with the list of icons, id, weapon name, required job, required level and given bonus.

It uses the propItem.txt file and some other files (including some .c file) so your Source is expected to not be too much differently organized from a regular v15 source.

An example generated file can be seen here http://sflyff.fr/items/

You need to convert yourself the .dss images in a .png format and put them in the Item folder in the same folder as the generated html file.

## delete_items.py

Don't use it

## delete_items_2.py

Reads `items_to_remove.txt`

This file format is
```
FIRST_WEAPON_ID_TO_DELETE
SECOND_WEAPON_ID_TO_DELETE
(...)
A_WEAPON_ID_TO_DELETE THE_WEAPON_THAT_WILL_RECEIVE_ITS_BONUS
```

A weapon can only receive bonus from one other weapon per pass. Order is not important. You can specify as many weapons as you like

This system should also work with other items

The new propItem will be written as a file named `newPropItem.txt``


## Usage

`python main.py /path/to/resource/folder NameOfYourPropItemFile NumberOfParameters(3 by default)`

Check the first lines of the py file to modify the base values.

## Requirements

Jinja2 is used to generate the pages : `pip install Jinja2`