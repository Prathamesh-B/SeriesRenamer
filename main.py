import os
import requests
from rich import print
from rich.progress import track
from rich.pretty import pprint
from rich.prompt import Prompt, IntPrompt, Confirm
import re
from tkinter import Tk, filedialog
import ascii_magic
import ssl

root = Tk()
root.withdraw()  # Hides small tkinter window.
root.attributes("-topmost", True)


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)


def validate_name(string: str) -> str:
    regex = re.compile('[/:*?<>|"]')
    if regex.search(string) == None:
        return string
    else:
        return re.sub('[/:*?<>|."]', "", string)


def get_info():
    print("Select Folder:")
    folder_location = filedialog.askdirectory()
    series_name = Prompt.ask("Name of Series", default=folder_location.split("/")[-1])
    season = IntPrompt.ask("Season Number")
    episode = IntPrompt.ask("Episode Number", default=1)
    return series_name, season, episode, folder_location

def check_show(show,season):
    # Check show exist 
    if len(show.json()["_embedded"]["seasons"]) < season:
        print(f'[bold red]Season {season} Not Found[/bold red]')
        try_again()


def check_ep(show,season,episode):
    # Check episodes exist and match no. of files
    index=1
    for i in show.json()["_embedded"]["seasons"]:
        if index == season:
                total_ep = i["episodeOrder"]
                
                if total_ep == None:
                    print("[bold yellow]Episodes names may not be available[/bold yellow]")
                elif total_ep != episode:
                    print(f'Season {season} Toatal Episodes {total_ep}')
                    print(f'Total Files in Folder {episode}')
                    print("[bold yellow]Warning! Total Episodes is !=  Total Files in Folder[/bold yellow]")
                else:
                    print(f'Season {season} Toatal Episodes {total_ep}')
        index+=1


def offline(series_name, season, episode, folder_location):
    file_list = sorted_alphanumeric(os.listdir(folder_location))
    # Confirm and continue
    print("[bold]Files Found[/bold]")
    pprint(file_list, expand_all=True)
    if Confirm.ask("Correct?", default=True):
        print()
        for file in track(file_list, description="Processing"):
            # construct current name using file name and path
            old_name = os.path.join(folder_location, file)

            if os.path.isdir(old_name):
                # skip directories
                continue

            # get file extension without name
            file_extention = os.path.splitext(file)[1]

            # Adding the new name with extension
            new_base = f"{series_name} S{season}E{str(episode)+file_extention}"
            # construct full file path
            new_name = os.path.join(folder_location, new_base)

            try:
                # renaming file
                os.rename(old_name, new_name)
            except FileExistsError:
                # printing error for already exists file
                print(f"[magenta]File with {new_base} already exists![/magenta]")
            finally:
                episode += 1

        # verify the result
        pprint("Done!")
        pprint(sorted_alphanumeric(os.listdir(folder_location)), expand_all=True)
        try_again()
    else:
        try_again()


def online(series_name, season, episode, folder_location):
    file_list = sorted_alphanumeric(os.listdir(folder_location))
    # Confirm and continue
    print("[bold]Files Found[/bold]")
    pprint(file_list, expand_all=True)
    if Confirm.ask("Correct?", default=True):
        print()
        try:
            if series_name.isnumeric():
                search = requests.get(f'https://api.tvmaze.com/shows/{series_name}?embed=seasons')
            else:
                search = requests.get(f"https://api.tvmaze.com/singlesearch/shows?q={series_name}&embed=seasons")
            if search.status_code == 200:
                show_id = search.json()["id"]
                image = search.json()["image"]
                if image != None:
                    ssl._create_default_https_context = ssl._create_unverified_context
                    my_art = ascii_magic.from_url(image["original"], columns=os.get_terminal_size()[0]-1)
                    ascii_magic.to_terminal(my_art)
                print(f'[bold]Name:[/bold] [cyan]{search.json()["name"]}[/cyan]')
                print(f'[bold]Total Episodes:[/bold] [cyan]{len(requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodes").json())}[/cyan]')
                print(f'[bold]Seasons:[/bold] [cyan]{len(search.json()["_embedded"]["seasons"])}[/cyan]')
                print(f'[bold]Release Date:[/bold] [cyan]{search.json()["premiered"]}[/cyan]')
                print(f'[bold]Type:[/bold] [cyan]{search.json()["type"]}[/cyan]')
                print(f'[bold]Language:[/bold] [cyan]{search.json()["language"]}[/cyan]')
                check_show(search,season) # Check show exist 
                check_ep(search,season,len(file_list)) # Check episodes exist and match no. of files
                if Confirm.ask("Correct?", default=True):
                    print()
                    for file in track(file_list, description="Processing"):
                        old_name = os.path.join(folder_location, file)
                        if os.path.isdir(old_name):
                            # skip directories
                            continue

                        # get episode info
                        episode_info = requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodebynumber?season={season}&number={episode}")
                        if episode_info.status_code == 200:
                            # get episode name and remove invaild renaming characters
                            episode_name = validate_name(episode_info.json()["name"])

                            # get file extension without name
                            file_extention = os.path.splitext(file)[1]

                            # Adding the new name with extension
                            new_base = (
                                f"{str(episode)} - {episode_name}{file_extention}"
                            )
                            # construct full file path
                            new_name = os.path.join(folder_location, new_base)

                            try:
                                # Renaming the file
                                os.rename(old_name, new_name)
                            except FileExistsError:
                                # printing error for already exists file
                                print(
                                    f"[magenta]File with {new_base} already exists![/magenta]"
                                )
                            finally:
                                episode += 1

                        else:
                            print("[bold red]Episode Not Found![/bold red]")

                    # verify the result
                    pprint("Done!")
                    pprint(
                        sorted_alphanumeric(os.listdir(folder_location)),
                        expand_all=True,
                    )
                    try_again()
                else:
                    try_again()
            else:
                print("[bold red]Show Not Found![/bold red]")
                try_again()
        except requests.exceptions.RequestException:
            print("[bold red]Check Internet Connection![/bold red]")
            try_again()
    else:
        try_again()


def main():
    choice = Prompt.ask("How you want to continue?", choices=["offline", "online"], default="offline")
    if choice == "offline":
        offline(*get_info())
    elif choice == "online":
        online(*get_info())


def try_again():
    choice = IntPrompt.ask(
        """
1- Exit
2- Retry
""",default=1,)
    if choice == 1:
        pprint("Bye!")
    elif choice == 2:
        main()


if __name__ == "__main__":
    main()
