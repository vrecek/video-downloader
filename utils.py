from App import App
from pytube.exceptions import AgeRestrictedError
import os


# File video download
def downloadListYT(APP: App, download_path: str) -> None:
    VID_FILE: str = 'videos.txt'
       
    # Create a file if its not present
    if not os.path.isfile(VID_FILE):
        open('videos.txt', 'a').close()
        APP.write('List "videos.txt" is empty')


    with open(VID_FILE, 'r') as file:
        # Read the URL from the file
        links: str = file.read()

        if not links:
            APP.write('List "videos.txt" is empty')

        links: list = links.split('\n')


    video_type: str = getInputVideoType()
    dwn_count:  int = 0
    links_len:  int = len(links)

    print()

    for i,x in enumerate(links):
        APP.write(f'Downloading {i + 1}/{links_len}', 'i')
        print()

        try:
            APP.downloadYoutube(x, download_path, video_type, quiet=True, raiseErr=True)
            dwn_count += 1

        except Exception as e:
            err: str = str(e)

            if 'AgeRestrictedError' in err:
                print()

            if 'RegexMatchError' in err:
                print ("\033[A\033[A")
                APP.write('Incorrect URL! Skipping...\n', 'i')

            continue

    APP.write(f'Done. Downloaded files: {dwn_count}/{links_len}', 'i')
    exit(0)



# Single video download
def downloadSingleYT(APP: App, url: str, download_path: str, filename: str) -> None:
    video_type: str = getInputVideoType()
        
    APP.downloadYoutube(url, download_path, video_type, filename=filename)



# Custom site download
def downloadSingleCustom(APP: App, url: str, download_path: str, filename: str) -> None:
    match APP.getBrowser():
        # Firefox / Librewolf
        case 'firefox' | 'librewolf':
            APP.downloadTagFirefox(url, filename, download_path)
            
        # Unknown browser
        case _:
            APP.write('Unknown browser') 



# Get the mp3/mp4 input
def getInputVideoType() -> str:
    return input('[INPUT] Select video type (mp3/mp4): ')