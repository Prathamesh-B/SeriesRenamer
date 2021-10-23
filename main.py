import os
from rich import print
from rich.progress import track
from rich.pretty import pprint
from rich.prompt import Prompt, IntPrompt
from rich.prompt import Confirm


def get_info():
    folder_name = input("Enter Folder: ")
    series_name = Prompt.ask("Name of Series", default=folder_name)
    season = IntPrompt.ask("Season Number")
    episode = IntPrompt.ask("Episode Number", default=1)
    folder = f"./{folder_name}"
    return series_name, season, episode, folder


def offline(series_name, season, episode, folder):
    # Confirm and continue
    pprint(os.listdir(folder), expand_all=True)
    if Confirm.ask("Correct?", default=True):
        print()
        for file in track(os.listdir(folder), description="Processing"):
            # construct current name using file name and path
            old_name = os.path.join(folder, file)

            if os.path.isdir(old_name):
                # skip directories
                continue

            # get file name without extension
            file_extention = os.path.splitext(file)[1]

            # Adding the new name with extension
            new_base = f"{series_name} S{season}E{str(episode)+file_extention}"
            # construct full file path
            new_name = os.path.join(folder, new_base)

            # Renaming the file
            os.rename(old_name, new_name)
            episode += 1

        # verify the result
        res = os.listdir(folder)
        pprint("Done!")
        pprint(res, expand_all=True)
        input("Enter to Exit")
    else:
        pprint("Bye!")
        input("Enter to Exit")


def online(series_name, season, episode, folder):
    import requests

    # Confirm and continue
    pprint(os.listdir(folder), expand_all=True)
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
                for file in track(os.listdir(folder), description="Processing"):
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

                        # get file extension
                        file_extention = os.path.splitext(file)[1]

                        # Adding the new name with extension
                        new_base = (
                            f"S{season}E{str(episode)} - {episode_name}{file_extention}"
                        )
                        # construct full file path
                        new_name = os.path.join(folder, new_base)

                        # Renaming the file
                        os.rename(old_name, new_name)
                        episode += 1

                    else:
                        print("[bold red]Episode Not Found![/bold red]")

                # verify the result
                res = os.listdir(folder)
                pprint("Done!")
                pprint(res, expand_all=True)
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
