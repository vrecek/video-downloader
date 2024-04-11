import os
import re
import subprocess
import shutil
import sys
from re import search
from urllib import error
from typing import Optional
from dotenv import load_dotenv
from sys import argv
from apiclient import discovery
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from pytube import YouTube, Stream, exceptions


class App():
    def __init__(self, env_file: str) -> None:
        load_dotenv(env_file)

        try:
            self.API_KEY   = os.getenv('API_KEY')
            self.ENGINE_ID = os.getenv('ENGINE_ID')

        except:
            self.write('Some of the environment variables are missing')



    def __getShell(self, inp: list) -> Optional[str]:
        return subprocess.run(inp, capture_output=True).stdout.decode('utf-8')


    def write(self, msg: str='Invalid option', type: str='e', terminate: bool=False) -> None:
        match type:
            case 'i': bar = '[INFO]'
            case 'e': bar = '[ERROR]'

        print(f'{bar} {msg}')

        if type == 'e' or terminate: 
            exit(1)


    def updateBrowserBinaries(self) -> None:
        p_browser: Optional[str] = os.getenv('BROWSER')
        p_driver:  Optional[str] = os.getenv('DRIVER')

        try:
            # Check for the firefox/librewolf browser
            if not p_browser:
                for x in ['firefox', 'librewolf']:
                    if self.__getShell(['which', x]).rstrip(): 
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

        self.write('Some of the browser binaries are missing. Please check the manual')


    def searchToDownloadFrom(self, links: list) -> str:
        providers: list = []

        # Check if the specified environment variables exist
        for x in links:
            var: Optional[str] = os.getenv(x)

            if not var:
                self.write('Some of the sites from the environment does not exist')

            providers.append(var)            


        self.write('Select the provider\n', 'i')
        for i, x in enumerate(links):
            print(f'[{i}] {x}')
            
        # Get the answer
        answer: str = input('\n>> ')
        print('')

        try:
            provider: str = providers[int(answer)]

            return provider

        except:
            self.write()


    def getArgs(self) -> str:
        if len(argv) < 2:
            self.write('Specify a video search query')

        # Get the query from argv
        return ' '.join(argv[1:])


    def openInBrowser(self, url: str) -> None:
        try:
            subprocess.Popen([self.browser, url], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        except:
            self.write('Browser was not found')


    def searchGoogle(self, query: str, site: str, result_num: int) -> Optional[list]:
        self.write('Searching...', 'i')

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
        self.write('Found video(s)', 'i')
        self.write('[INFO] Select number and [d]ownload, [o]pen\n', 'i')

        # Display possible videos
        for i, [title, url] in enumerate(results):
            print(f'[{i}] {title}')

        # Get the answer
        answer: str = input('\n>> ')
        print('')

        # Answer must be: <number><type>
        if len(answer) != 2:
            self.write()

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
                    self.write()
            
            return selected_url, option

        except Exception as e:
            self.write()


    def downloadYoutube(self, url: str, dwn_path: str, vid_type: str, filename: str=None, quiet: bool=False, raiseErr: bool=False) -> None:
        def on_progress(stream: Stream, _, remaining: int) -> None:
            # Calculate the current %
            perc: int = round((1 - remaining / stream.filesize) * 100)

            # Clear previous line
            print ("\033[A\033[A")

            # Make a progress bar
            print(f"|{'=' * perc}{' ' * (100 - perc)}| {perc}%")


        try:
            not quiet and self.write('Fetching...', 'i')
            yt = YouTube(url, on_progress).streams

        # When client=ANDROID_EMBED + age restricted video
        except exceptions.AgeRestrictedError:
            # Find the local python version
            libpath: str = os.path.join(os.path.expanduser('~'), '.local', 'lib')
            py_ver:  str = f'{sys.version_info[0]}.{sys.version_info[1]}'

            try:
                # And find the pytube package
                pylib: str = [v for v in os.listdir(libpath) if search(rf'^python{py_ver}', v)][0]
                f:     str = os.path.join(libpath, pylib, 'site-packages', 'pytube', '__main__.py')

                with open(f, 'r+') as file:
                    # Replace value due to the bug in the package?
                    new: str = file.read().replace('ANDROID_EMBED', 'ANDROID_CREATOR')

                    file.seek(0)
                    file.write(new)
                    file.truncate()

                self.write('Age restricted video detected for the first time. Please re-run the script to apply necessary changes', 'i', True)

            except IndexError:
                self.write(
                    'Unknown python version. Please edit "~/.local/lib/<version>/site-packages/pytube/__main__.py" client=ANDROID_EMBED to client=ANDROID_CREATOR'
                )

        # When client=ANDROID_CREATOR + age restricted video 
        except KeyError:
            self.write('Video is age restricted', 'i')
            age_input: str = input('[INPUT] Would you like to use your verified Google account? (y/n): ')

            if age_input != 'y':
                if raiseErr:
                    raise exceptions.AgeRestrictedError

                self.write('Video is age restricted')

            print()

            try:
                yt = YouTube(url, on_progress, use_oauth=True, allow_oauth_cache=True).streams

            except error.HTTPError:
                self.write('Authentication failed')
        
        # Unknown error
        except exceptions.RegexMatchError as e:
            if raiseErr:
                raise exceptions.RegexMatchError
                
            self.write('Unknown error. Make sure the video is correct')


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
                self.write()


        not quiet and self.write('Downloading...\n\n', 'i')

        escaped_title: str = yt.title.replace('/', '-')

        yt.download(dwn_path, f'{filename or escaped_title}.{vid_type}')
        print('')


    def downloadTagFirefox(self, url: str, filename: str, dwn_path: str) -> None:
        self.write('Starting driver...', 'i')

        # Selenium Firefox
        options = Options()

        options.binary_location = self.browser
        options.add_argument('--headless')


        # Initialize the geckodriver
        try:
            service = Service(self.driver)

            driver: any = webdriver.Firefox(service=service, options=options)
            driver.get(url)

        except:
            self.write('Geckodriver/Browser was not found')


        try:
            # Get the actual video URL
            mp4: str = re.search(r'<video.*?src="(.*?)".*?></video>', driver.page_source).group(1)

            # Download a file using wget
            self.write('Downloading...\n', 'i')
            subprocess.call(['wget', '--user-agent="Mozilla"', '-O', f'{dwn_path}/{filename}.mp4', mp4])

        except AttributeError:
            driver.quit()
            self.write('Could not find a video URL')
            
        finally:
            driver.quit()


    def getBrowser(self) -> Optional[str]:
        return self.browser
