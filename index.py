import subprocess
import os
import signal
from App import App
from typing import Optional
from utils import downloadSingleYT, downloadSingleCustom
from pathlib import Path


signal.signal(signal.SIGINT, lambda sig,frame: exit(0))


APP:      App = App('.env')
QUERY:    str = APP.getArgs()
DWN_PATH: str = Path.home()


# Download from the videos.txt
if QUERY == 'dl':
    APP.downloadListYoutube(DWN_PATH)


SITE:        str  = APP.searchToDownloadFrom(['SITE_1', 'SITE_2'])
FILENAME:    str  = QUERY.replace(' ', '_')
MAX_RESULTS: int  = 5


# Search through a google custom search engine
results: Optional[list] = APP.searchGoogle(QUERY, SITE, MAX_RESULTS)

if not results:
    APP.write('Video not found. Try a different query')


# Let the user select the video
url, option = APP.handleSelectMenu(results)

# Update and check the browser binaries
APP.updateBrowserBinaries()
APP.checkBrowserBinaries()


# Open in the browser
if option == 'open':
    APP.openInBrowser(url)

# Or download the video
elif option == 'download':
    # Download from SITE_1
    if SITE == os.getenv('SITE_1'):
        downloadSingleCustom(APP, url, DWN_PATH, FILENAME)

    # Download from SITE_2
    elif SITE == os.getenv('SITE_2'):
        downloadSingleYT(APP, url, DWN_PATH, FILENAME)

    # Invalid site
    else:
        APP.write('Incorrect site to download from')
