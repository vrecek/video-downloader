# Video downloader

It's using pytube for the Youtube videos

# Other sites

It also supports sites that have a video tag source that points to an embeded player, that points directly to mp4. <br>
site -> embeded video -> mp4 file <br>

# Usage

```pip install -r requirements.txt``` <br>

##### Search query

```python3 index.py <query>```<br>

##### Download from the videos.txt file

```python3 index.py dl```<br>

In your .env file create site name with the source, eg. SITE_2=youtube.com <br>
In "if" statements, by default it's using SITE_1 as 'other site' and SITE_2 as 'youtube'

# .env

API_KEY -> google programmable search engine API key <br>
ENGINE_ID -> ID of your google engine <br>
-site name- -> eg. MYSITE=somesite.com <br>
BROWSER -> optional browser (firefox/librewolf)
DRIVER -> optional geckodriver path <br>

# Troubleshooting

##### Browser was not found

Make sure to set "BROWSER=-name-" in your .env file. -name- may be firefox or librewolf

##### Geckodriver/Browser was not found

Make sure to set both "BROWSER=-name-" and "DRIVER=-path-" in your .env file. -name- may be firefox or librewolf, -path- is a path to the geckodriver

##### List "videos.txt" is empty

Make sure to include YT URLs in the videos.txt file

##### Video is age restricted

Make sure to use your own verified Google account when prompted
