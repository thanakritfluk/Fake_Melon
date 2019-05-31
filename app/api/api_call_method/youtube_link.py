import urllib.parse
import urllib.request as request_url
from bs4 import BeautifulSoup


def url_music(track_name):
    query = urllib.parse.quote(track_name)
    youtube_url = "https://www.youtube.com/results?search_query=" + query
    response = request_url.urlopen(youtube_url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
        try:
            return 'https://www.youtube.com/' + vid['href']
        except:
            return "NONE"
