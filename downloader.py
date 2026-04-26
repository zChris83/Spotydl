import os, sys
import time
from ytmusicapi import YTMusic
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp


# --- Spotify Auth ---
auth_manager = SpotifyClientCredentials(
    client_id="c8a82d1ba62443cf8a6f04d52be699d1",
    client_secret="edfe50055545418daabb608948a01365"
)
sp = Spotify(auth_manager=auth_manager)

def my_hook(d):
    if d['status'] == 'downloading':
        print("Downloading: ", end='')
        sys.stdout.flush()
    if d['status'] == 'finished':
        try:
            print(": ",d['info_dict']['title'],'-',d['info_dict']['artists'][0])
        except KeyError:
            print(": ",d['info_dict']['title'])


# --- YouTube Audio Download using yt-dlp ---
def downloadMP3(url, path, filename):
    filename = filename.replace('?', '')  # Clean filename
    filename = filename.replace('/','')  # So it does not create folders.
    output_path = os.path.join(path, f"{filename}.%(ext)s")

    if not os.path.exists(os.path.join(path, f"{filename}.mp3")):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'noprogress': False,  # keep progress bar
            'progress_with_newline': False,  # cleaner look
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'progress_hooks': [my_hook]
        }

        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

# --- YouTube Music Search ---
def ytMusicSearch(query):
    ytm = YTMusic()
    search_results = ytm.search(f"{query[0]} - {query[1]}", filter="songs")
    if search_results:
        result = search_results[0]
        print("Found:",result["title"], "-", result["artists"][0]["name"])
        return f"https://www.youtube.com/watch?v={result['videoId']}"
    else:
        print("Could not download:", f"{query[0]} - {query[1]}")
        return "FAIL"

# --- Spotify Playlist to Song List ---
def spotifyPlaylist(url):
    songs = []
    offset = 0
    playlist_id = url.split("/")[-1].split("?")[0]
    items = list()
    items2 = list()
    while True:
        items2.clear()
        items2 = sp.playlist_items(playlist_id,None,100,offset)["items"]
        for item in items2:
            items.append(item)
        offset = offset + 100
        if len(items2) < 100:
            break
    
    for item in items:
        name = item["track"]["name"]
        artist = item["track"]["artists"][0]["name"]
        songs.append((name, artist))
    return songs

# --- Full Playlist Downloader ---
def downloadFromSpotifyPlaylist(url, path):
    failed = []
    start = time.time()
    os.makedirs(path, exist_ok=True)
    songs = spotifyPlaylist(url)
    i = 0
    for name, artist in songs:
        i = i+1
        print(f"\nSearching: {name} - {artist}")
        filename = f"{name} - {artist}.mp3"
        filename = filename.replace('?', '')  # Clean filename
        filename = filename.replace('/','')  # So it does not create folders.
        if os.path.exists(os.path.join(path, f"{filename}")):
            print("EXISTS")
        else:
            yt_url = ytMusicSearch((name, artist))
            if yt_url != "FAIL":
                downloadMP3(yt_url, path, f"{name} - {artist}")
            else:
                failed.append(f"{name} - {artist}")
    
    end = time.time()
    print(f"\nDownload complete in {round(end - start, 2)} seconds. Processed {i} songs")
    if failed:
        print("Failed to download:")
        for f in failed:
            print(f" - {f}")

# --- Manual Download (YouTube URL only) ---
def downloadManually(url, path, song):
    downloadMP3(url, path, song)

