import os
from rich.progress import track
from rich.pretty import pprint
from rich.prompt import Prompt, IntPrompt
from rich.prompt import Confirm

folder_name = input("Enter Folder: ")
series_name = Prompt.ask("Name of Series", default=folder_name)
season = input("Season Number: ")
episode = IntPrompt.ask("Episode Number", default=1) - 1
folder = f"./{folder_name}/"

# Confirm and continue
pprint(os.listdir(folder), expand_all=True)
if Confirm.ask("Correct?", default=True):
    print()
    for file in track(os.listdir(folder), description="Processing"):
        episode += 1
        # construct current name using file name and path
        old_name = os.path.join(folder, file)
        # get file name without extension
        file_extention = os.path.splitext(file)[1]

        # Adding the new name with extension
        new_base = f"{series_name} S{season}E{str(episode)+file_extention}"
        # construct full file path
        new_name = os.path.join(folder, new_base)

        # Renaming the file
        os.rename(old_name, new_name)

    # verify the result
    res = os.listdir(folder)
    pprint("Done!")
    pprint(res, expand_all=True)
    input("Enter to Exit")
else:
    pprint("Bye!")
    input("Enter to Exit")
