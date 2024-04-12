from App import App



# Single video download
def downloadSingleYT(APP: App, url: str, download_path: str, filename: str) -> None:
    video_type: str = APP.getInputVideoType()
        
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


