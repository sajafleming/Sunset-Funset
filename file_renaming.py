"""Renaming img files"""

from os import rename, listdir

ORIGIN_DIRECTORY = "/Users/Sarah/PROJECT/TNMDownloadManager/"
DESTINATION_DIRECTORY = "/Users/Sarah/PROJECT/imgfiles/"

for dir_name in listdir(ORIGIN_DIRECTORY):
    if "USGS" not in dir_name:
        continue
    for name in listdir(ORIGIN_DIRECTORY + dir_name):
        if not name.endswith(".img"):
            continue

        new_name = name[3:-6]

        # rename file
        rename(ORIGIN_DIRECTORY + dir_name + "/" + name,
            DESTINATION_DIRECTORY + new_name + ".img")
