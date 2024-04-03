# Video downloader
Download videos from a many sites <br>
It's using pytube for Youtube handling

# Other sites
It also supports sites that have a video tag source that points to an embeded player, that points directly to mp4. <br>
site -> embeded video -> mp4 file <br>

# Usage
```pip install -r requirements.txt``` <br>
```python3 index.py <query>```<br>
In your .env file create a site(s) name with the source, eg. MYSITE=somesite.com <br> 
Then in APP.searchToDownloadFrom([]) place your variable(s) name <br>
Finally in "elif" statements replace os.getenv() with your variable(s) name <br>

# .env
API_KEY -> google programmable search engine API key <br>
ENGINE_ID -> ID of your google engine <br>
DOWNLOAD_PATH -> path where the files will be downloaded to <br> 

-site name- -> download site, eg. MYSITE=somesite.com <br>

DRIVER -> optional geckodriver path <br>
BROWSER -> optional browser (firefox/librewolf)
