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


class App():
    def __init__(self, env_file: str) -> None:
        load_dotenv(env_file)

        try:
            self.API_KEY = os.getenv('API_KEY')
            self.ENGINE_ID = os.getenv('ENGINE_ID')

            self.sites = [
                os.getenv('SITE_1'),
                os.getenv('SITE_2')
            ]

        except:
            print('[ERROR] Some of the environment variables are missing')
            exit(1)


    def __exit(self, msg: str = 'Invalid option') -> None:
        print(f'[ERROR] {msg}')
        exit(1)

    def __getShell(self, inp: list) -> Optional[str]:
        return subprocess.run(inp, capture_output=True).stdout.decode('utf-8')


    def updateBrowserBinaries(self) -> Optional[str]:
        browser_name: Optional[str] = None

        try:
            # Check for the firefox/librewolf browser
            for x in ['firefox', 'librewolf']:
                browser: Optional[str] = self.__getShell(['which', x]).rstrip()

                if browser: 
                    browser_name = x
                    break


            # Check for the browser driver
            for x in ['geckodriver']:
                driver: Optional[str] = self.__getShell(['locate', 'geckodriver']).split('\n')
                driver = shutil.which(driver[0])

                if driver: break
                

            self.driver  = driver  or None
            self.browser = browser or None

        except:
            self.driver  = None
            self.browser = None

        finally:
            return browser_name


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
            self.__exit('Browser was not found')


    def searchGoogle(self, query: str, site: str) -> Optional[list]:
        print('[INFO] Searching...')

        # Search from the specific sites
        if not site in self.sites:
            self.__exit('Incorrect site selection')

        index: int = self.sites.index(site) 
        query = f'{query} site:{self.sites[index]}'

        # Search from the google custom search
        resource: any  = discovery.build('customsearch', 'v1', developerKey=self.API_KEY).cse()
        result:   dict = resource.list(q=query, cx=self.ENGINE_ID, num=3).execute()


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


    def downloadYoutube(self, url: str) -> None:
        pass


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
            self.__exit('Browser was not found')


        try:
            # Get the actual video URL
            mp4: str = re.search(r'<video.*?src="(.*?)".*?></video>', driver.page_source).group(1)

            # Download a file using wget
            print('[INFO] Downloading...\n')
            subprocess.call(['wget', '--user-agent="Mozilla"', '-O', f'{dwn_path}/{filename}.mp4', mp4])

        except AttributeError:
            print('[ERROR] Could not find a video URL')

        except KeyboardInterrupt:
            print('[EXIT] Interrupted')
            
        finally:
            driver.quit()