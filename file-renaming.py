"""Move img files to one spot"""

from os import rename, listdir

def rename_files(list_of_filenames):

    for name in list_of_filenames:
        new_name = name[3:-6]

        # rename file
        rename("/Users/Sarah/PROJECT/imgfiles/" + name, "/Users/Sarah/PROJECT/imgfiles/" + new_name + ".img")

list_of_filenames = listdir("/Users/Sarah/PROJECT/imgfiles/")
    
rename_files(list_of_filenames)