"""Renaming img files"""

from os import listdir
from shutil import copyfile

ORIGIN_DIRECTORY = "/Users/Sarah/PROJECT/data/ai/"
DESTINATION_DIRECTORY = "/Users/Sarah/PROJECT/data/ai_img/"

for dir_name in listdir(ORIGIN_DIRECTORY):
    if "USGS" not in dir_name:
        continue
    for name in listdir(ORIGIN_DIRECTORY + dir_name):
        if not name.endswith(".img"):
            continue

        if len(name) == 16:
            new_name = name[3:-6]
        elif len(name) == 26:
            new_name = name[11:-8]

        # rename file
        copyfile(ORIGIN_DIRECTORY + dir_name + "/" + name,
            DESTINATION_DIRECTORY + new_name + ".img")


# two formats
# imgn34w089_1.img -> len 16
# USGS_NED_1_n31w084_IMG.img -> len 26