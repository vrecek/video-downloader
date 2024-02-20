# Video downloader
Download videos from Youtube and other sites <br>

# Other sites
Besides Youtube, it supports sites that have a video tag source that points to embeded player, that points directly to mp4. <br>
site -> embeded video -> mp4 file <br>

# Usage
```pip install -r requirements.txt``` <br>
```python3 index.py <query>```<br>
In your .env file create a site(s) name with the source, eg. YOUTUBE=youtube.com <br> 
Then in APP.searchToDownloadFrom([]) place your site name <br>
Finally in "elif" statements replace os.getenv() with your site name <br>
By default SITE_2 is Youtube, and SITE_1 is the embeded/mp4 video

# .env
API_KEY -> google programmable search engine API key <br>
ENGINE_ID -> ID of your google engine <br>
DOWNLOAD_PATH -> path where the files will be downloaded to <br> 

-site name- -> download site, eg. YOUTUBE=youtube.com <br>

DRIVER -> optional geckodriver path <br>
BROWSER -> optional browser (firefox/librewolf)
