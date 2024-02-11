import re
import subprocess
import os
from time import sleep
from sys import argv
from apiclient import discovery
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv


# Get the query
if len(argv) < 2:
    print('[ERROR] Specify a video name')
    exit(1)


load_dotenv('.env')


args:     list = argv[1:]

QUERY:    str  = f"{' '.join(args)} {os.getenv('SITE_1')}"
API_KEY:  str  = os.getenv('API_KEY')
ENG_KEY:  str  = os.getenv('ENGINE_ID')


# Search through a google custom search engine
print('[INFO] Searching...')
resource      = discovery.build('customsearch', 'v1', developerKey=API_KEY).cse()
result:  dict = resource.list(q=QUERY, cx=ENG_KEY, num=1).execute()


# Exit if a video was not found
if not 'items' in result:
    print("[ERROR] Video not found. Try a different query")
    exit(2)


# Grab the title and the url
result = result['items'][0]

title:   str  = result['title']
url:     str  = result['link']

confirm: str  = input(f'[INFO] Found video: "{title}". Do you want to download it? [y]es/[n]o/[o]pen -> ')


# Confirm the user decision
if confirm == 'o':
    subprocess.Popen(['firefox', url], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    exit(0)

if confirm != 'y':
    exit(0)


print('[INFO] Starting driver...')

# Selenium Firefox
options = Options()
options.add_argument('--headless')

# Init the geckodriver path
service = Service('/usr/local/bin/geckodriver')

# Launch an actual driver and fetch the HTML
driver  = webdriver.Firefox(service=service, options=options)
driver.get(url)


print('[INFO] Loading video...')
sleep(2)


try:
    # Get the actual video URL
    mp4:      str = re.search(r'<video.*?src="(.*?)".*?></video>', driver.page_source).group(1)
    dwn_path: str = '/home/vrecek/Downloads'

    # Download a file using wget
    print('[INFO] Downloading...')
    subprocess.call(['wget', '--user-agent="Mozilla"', '-O', f'{dwn_path}/{"_".join(args)}.mp4', mp4])

except AttributeError:
    print('[ERROR] Could not find a video URL')
    
finally:
    driver.quit()