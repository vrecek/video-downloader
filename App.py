import os
import re
import subprocess
import shutil
from typing import Optional
from dotenv import load_dotenv
from sys import argv
from apiclient import discovery
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from pytube import YouTube, Stream


class App():
    def __init__(self, env_file: str) -> None:
        load_dotenv(env_file)

        try:
            self.API_KEY   = os.getenv('API_KEY')
            self.ENGINE_ID = os.getenv('ENGINE_ID')

        except:
            print('[ERROR] Some of the environment variables are missing')
            exit(1)


    def __exit(self, msg: str = 'Invalid option') -> None:
        print(f'[ERROR] {msg}')
        exit(1)

    def __getShell(self, inp: list) -> Optional[str]:
        return subprocess.run(inp, capture_output=True).stdout.decode('utf-8')



    def updateBrowserBinaries(self) -> None:
        p_browser: Optional[str] = os.getenv('BROWSER')
        p_driver:  Optional[str] = os.getenv('DRIVER')


        try:
            # Check for the firefox/librewolf browser
            if not p_browser:
                for x in ['firefox', 'librewolf']:
                    browser: Optional[str] = self.__getShell(['which', x]).rstrip()

                    if browser: 
                        p_browser = x
                        break


            # Check for the browser driver
            if not p_driver:
                for x in ['geckodriver']:
                    driver: Optional[str] = self.__getShell(['locate', 'geckodriver']).split('\n')
                    driver = shutil.which(driver[0])

                    if driver: 
                        p_driver = driver
                        break
                

            self.driver  = p_driver
            self.browser = p_browser

        except:
            self.driver  = None
            self.browser = None


    def checkBrowserBinaries(self) -> None:
        if all([self.browser, self.driver]):
            return

        self.__exit('Some of the browser binaries are missing. Please check the manual')


    def searchToDownloadFrom(self, links: list) -> str:
        providers: list = []

        # Check if the specified environment variables exist
        for x in links:
            var: Optional[str] = os.getenv(x)

            if not var:
                self.__exit('Some of the sites from the environment does not exist')

            providers.append(var)            


        print("""[INFO] Select the provider\n""")
        for i, x in enumerate(links):
            print(f'[{i}] {x}')
            
        # Get the answer
        answer: str = input('\n>> ')
        print('')

        try:
            provider: str = providers[int(answer)]

            return provider

        except:
            self.__exit('Incorrect option')


    def getArgs(self) -> str:
        if len(argv) < 2:
            print('[ERROR] Specify a video search query')
            exit(1)

        # Get the query from argv
        return ' '.join(argv[1:])


    def openInBrowser(self, url: str) -> None:
        try:
            subprocess.Popen([self.browser, url], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        except:
            self.__exit('[ERROR] Browser was not found')


    def searchGoogle(self, query: str, site: str, result_num: int) -> Optional[list]:
        print('[INFO] Searching...')

        # Search from the specific site
        query = f'{query} site:{site}'

        # Search from the google custom search
        resource: any  = discovery.build('customsearch', 'v1', developerKey=self.API_KEY).cse()
        result:   dict = resource.list(q=query, cx=self.ENGINE_ID, num=result_num).execute()


        if not 'items' in result:
            return None

        # Return the array of titles/links
        return [ [x['title'], x['link']] for x in result['items'] ]


    def handleSelectMenu(self, results: list) -> str:
        print("""[INFO] Found video(s)""")
        print("""[INFO] Select number and [d]ownload, [o]pen\n""")

        # Display possible videos
        for i, [title, url] in enumerate(results):
            print(f'[{i}] {title}')

        # Get the answer
        answer: str = input('\n>> ')
        print('')

        # Answer must be: <number><type>
        if len(answer) != 2:
            self.__exit()


        nr, opt = answer

        try:
            # Get the url and the action type from the input
            selected_url: str = results[int(nr)][1]
        
            match (opt):
                case 'o':
                    option = 'open'
                case 'd':
                    option = 'download'
                case _:
                    self.__exit()

            return selected_url, option

        except:
            self.__exit()


    def downloadYoutube(self, url: str, filename: str, dwn_path: str, vid_type: str) -> None:
        def on_progress(stream: Stream, _, remaining: int) -> None:
            # Calculate the current %
            perc: int = round((1 - remaining / stream.filesize) * 100)

            # Clear previous 3 lines
            print ("\033[A\033[A")
            print ("\033[A\033[A")
            print ("\033[A\033[A")

            # Make a progress bar
            print('-' * 100)
            print(f'{"=" * perc}{" " * (100 - perc)} {perc}%')
            print('-' * 100)


        print('[INFO] Fetching...')
        yt = YouTube(url, on_progress).streams

        match vid_type:
            case 'mp3':
                yt = yt.filter(only_audio=True) \
                       .first()

            case 'mp4':
                yt = yt.filter(progressive=True, file_extension='mp4') \
                       .order_by('resolution') \
                       .desc() \
                       .first()
            case _:
                self.__exit()

        print('[INFO] Downloading...\n\n\n')
        yt.download(dwn_path, f'{filename}.{vid_type}')


    def downloadTagFirefox(self, url: str, filename: str, dwn_path: str) -> None:
        print('[INFO] Starting driver...')

        # Selenium Firefox
        options = Options()

        options.binary_location = self.browser
        options.add_argument('--headless')


        # Initialize the geckodriver
        try:
            service = Service(self.driver)

        except:
            self.__exit('Geckodriver was not found')


        # Launch an actual driver and fetch the HTML
        try:
            driver: any = webdriver.Firefox(service=service, options=options)
            driver.get(url)

        except:
            self.__exit('Geckodriver/Browser was not found')


        try:
            # Get the actual video URL
            mp4: str = re.search(r'<video.*?src="(.*?)".*?></video>', driver.page_source).group(1)

            # Download a file using wget
            print('[INFO] Downloading...\n')
            subprocess.call(['wget', '--user-agent="Mozilla"', '-O', f'{dwn_path}/{filename}.mp4', mp4])

        except AttributeError:
            print('[ERROR] Could not find a video URL')
            
        finally:
            driver.quit()


    def getBrowser(self) -> Optional[str]:
        return self.browser
