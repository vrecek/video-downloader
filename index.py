import subprocess
import os
import signal
from App import App
from typing import Optional


signal.signal(signal.SIGINT, lambda sig,frame: exit(0))


APP           = App('.env')

QUERY:    str = APP.getArgs()
FILENAME: str = QUERY.replace(' ', '_')
DWN_PATH: str = '/home/vrecek/Downloads'
SITE:     str = APP.searchToDownloadFrom(['SITE_1', 'SITE_2'])


# Search through a google custom search engine
results: Optional[list] = APP.searchGoogle(QUERY, SITE)

if not results:
    print("[ERROR] Video not found. Try a different query")
    exit(0)


# Get the user input
url, option  = APP.handleSelectMenu(results)

# Determine the user's browser
browser: str = APP.updateBrowserBinaries()


# Open in the browser
# Or download the video
if option == 'open':
    APP.openInBrowser(url)

elif option == 'download':

    # Custom site to download from
    if SITE == os.getenv('SITE_1'):
        match (browser):
            # Firefox / Librewolf
            case 'firefox' | 'librewolf':
                APP.downloadTagFirefox(url, FILENAME, DWN_PATH)
                
            # Unknown browser
            case _:
                print('Unknown browser')        


    # Download from YouTube
    elif SITE == os.getenv('SITE_2'):
        APP.downloadYoutube(url, FILENAME, DWN_PATH)

    # Invalid site
    else:
        print('[ERROR] Incorrect site to download from')