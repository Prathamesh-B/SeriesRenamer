import os
from rich import print
from rich.progress import track
from rich.pretty import pprint
from rich.prompt import Prompt, IntPrompt
from rich.prompt import Confirm
import re


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(data, key=alphanum_key)


def get_info():
    folder_name = input("Enter Folder: ")
    series_name = Prompt.ask("Name of Series", default=folder_name)
    season = IntPrompt.ask("Season Number")
    episode = IntPrompt.ask("Episode Number", default=1)
    folder = f"./{folder_name}"
    return series_name, season, episode, folder


def offline(series_name, season, episode, folder):
    file_list = sorted_alphanumeric(os.listdir(folder))
    # Confirm and continue
    print("[bold]Files Found[/bold]")
    pprint(file_list, expand_all=True)
    if Confirm.ask("Correct?", default=True):
        print()
        for file in track(file_list, description="Processing"):
            # construct current name using file name and path
            old_name = os.path.join(folder, file)

            if os.path.isdir(old_name):
                # skip directories
                continue

            # get file extension without name
            file_extention = os.path.splitext(file)[1]

            # Adding the new name with extension
            new_base = f"{series_name} S{season}E{str(episode)+file_extention}"
            # construct full file path
            new_name = os.path.join(folder, new_base)

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
        pprint(sorted_alphanumeric(os.listdir(folder)), expand_all=True)
        input("Enter to Exit")
    else:
        pprint("Bye!")
        input("Enter to Exit")


def online(series_name, season, episode, folder):
    import requests

    file_list = sorted_alphanumeric(os.listdir(folder))
    # Confirm and continue
    print("[bold]Files Found[/bold]")
    pprint(file_list, expand_all=True)
    if Confirm.ask("Correct?", default=True):
        print()
        search = requests.get(
            f"https://api.tvmaze.com/singlesearch/shows?q={series_name}"
        )
        if search.status_code == 200:
            show_id = search.json()["id"]
            print(f'[bold]Name:[/bold] [cyan]{search.json()["name"]}[/cyan]')
            print(
                f'[bold]Episodes:[/bold] [cyan]{len(requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodes").json())}[/cyan]'
            )
            print(f'[bold]Release:[/bold] [cyan]{search.json()["premiered"]}[/cyan]')
            print(f'[bold]Type:[/bold] [cyan]{search.json()["type"]}[/cyan]')
            print(f'[bold]Lang:[/bold] [cyan]{search.json()["language"]}[/cyan]')
            if Confirm.ask("Correct?", default=True):
                print()
                for file in track(file_list, description="Processing"):
                    old_name = os.path.join(folder, file)
                    if os.path.isdir(old_name):
                        # skip directories
                        continue

                    # get episode info
                    episode_info = requests.get(
                        f"https://api.tvmaze.com/shows/{show_id}/episodebynumber?season={season}&number={episode}"
                    )
                    if episode_info.status_code == 200:
                        episode_name = episode_info.json()["name"]

                        # get file extension without name
                        file_extention = os.path.splitext(file)[1]

                        # Adding the new name with extension
                        new_base = f"{str(episode)} - {episode_name}{file_extention}"
                        # construct full file path
                        new_name = os.path.join(folder, new_base)

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
                pprint(sorted_alphanumeric(os.listdir(folder)), expand_all=True)
                input("Enter to Exit")
        else:
            print("[bold red]Not Found![/bold red]")
    else:
        pprint("Bye!")
        input("Enter to Exit")


if __name__ == "__main__":
    choice = Prompt.ask(
        "How you want to continue?", choices=["offline", "online"], default="offline"
    )
    if choice == "offline":
        offline(*get_info())
    elif choice == "online":
        online(*get_info())
