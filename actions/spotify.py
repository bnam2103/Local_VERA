import subprocess
import webbrowser
import requests
import base64
import pyautogui
import time

CLIENT_ID = "582b8a391601439489aac9f94ea6c048"
CLIENT_SECRET = "5ade39e3e78a49dd8354316e13950e62"

def get_access_token():
    url = "https://accounts.spotify.com/api/token"

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    token_data = response.json()
    access_token = token_data["access_token"]
    print("Token:", access_token)
    print("Expires in:", token_data["expires_in"])
    return access_token

# def open_spotify_artist_page(artist_name, access_token):
#     """
#     Opens the Spotify page of the given artist in the default web browser.
#     """
#     # Search for the artist on Spotify
#     response = requests.get(
#         'https://api.spotify.com/v1/search',
#         headers={'Authorization': f'Bearer {access_token}'},
#         params={'q': artist_name, 'type': 'artist', 'limit': 1}  # limit=1 for the first match
#     )

#     if response.status_code != 200:
#         print(f"Error fetching artist: {response.status_code}")
#         return

#     data = response.json()

#     # Check if any artists were found
#     if 'artists' in data and data['artists']['items']:
#         artist = data['artists']['items'][0]  # take the first match
#         spotify_url = artist['external_urls']['spotify']
#         print(f"Opening {artist['name']}'s Spotify page: {spotify_url}")
#         webbrowser.open(spotify_url)
#     else:
#         print(f"No artist found for '{artist_name}'")

def get_spotify_track_uri(track_name, artist_name, access_token):
    """
    Returns the Spotify URI of a track given its name and artist.
    
    track_name: Name of the song
    artist_name: Name of the artist
    access_token: Spotify OAuth token
    """
    query = f"track:{track_name} artist:{artist_name}"
    url = "https://api.spotify.com/v1/search"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {
        "q": query,
        "type": "track",
        "limit": 1  # Only need the top match
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching track: {response.status_code}")
        return None
    
    data = response.json()
    items = data.get("tracks", {}).get("items")
    
    if not items:
        print("No track found for that name and artist.")
        return None
    
    return items[0]["uri"]  # Spotify URI of the first match

def play_spotify_song(track_uri):
    webbrowser.open(track_uri)

def open_spotify():
    subprocess.Popen(["spotify"])  # On Windows or Linux if installed
    print("Spotify opened.")

def close_spotify():
    if subprocess.run(["tasklist"], capture_output=True, text=True).stdout.find("Spotify.exe") != -1:
        subprocess.run(["taskkill", "/IM", "Spotify.exe", "/F"])
        print("Spotify closed.")
    else:
        print("Spotify is not running.")

def pause_spotify():
    """
    Toggle Spotify playback using the spacebar.
    """
    # Make sure Spotify is the active window
    # Optionally, you can use pygetwindow to focus Spotify
    pyautogui.press("space")
    print("Toggled playback (play/pause)")

def increase_volume():
    pyautogui.press("volumeup")
    pyautogui.press("volumeup")
    pyautogui.press("volumeup")
    pyautogui.press("volumeup")
    pyautogui.press("volumeup")
    pyautogui.press("volumeup")
    print("Increased volume.")

def decrease_volume():
    pyautogui.press("volumedown")
    pyautogui.press("volumedown")
    pyautogui.press("volumedown")
    pyautogui.press("volumedown")
    pyautogui.press("volumedown")
    pyautogui.press("volumedown")

    print("Decreased volume.")

def mute():
    pyautogui.press("volumemute")
    print("Muted volume.")


# def is_spotify_paused(access_token):
#     """
#     Checks Spotify playback state.
    
#     Returns:
#         paused (bool): True if Spotify is paused, False if playing or nothing playing.
#         info (str): Info about the current track or error message.
    
#     access_token: Spotify OAuth token with 'user-read-playback-state' scope
#     """
#     url = "https://api.spotify.com/v1/me/player"
#     headers = {"Authorization": f"Bearer {access_token}"}
    
#     response = requests.get(url, headers=headers)
    
#     if response.status_code == 200:
#         playback_state = response.json()
#         if playback_state is None or not playback_state.get("item"):
#             return False, "Nothing is currently playing."
        
#         is_playing = playback_state.get("is_playing", False)
#         current_track = playback_state["item"]["name"]
#         artist = playback_state["item"]["artists"][0]["name"]
        
#         if is_playing:
#             return False, f"Currently playing: {current_track} by {artist}"
#         else:
#             return True, f"Playback is paused: {current_track} by {artist}"
    
#     elif response.status_code == 204:
#         # No content → nothing is playing
#         return False, "Nothing is currently playing."
    
#     elif response.status_code == 404:
#         return False, "No active Spotify device found. Make sure Spotify is open and logged in with this account."
    
#     else:
#         try:
#             error_info = response.json()
#         except ValueError:
#             error_info = response.text
#         return False, f"Error fetching playback state: {response.status_code} - {error_info}"


# Example usage
# open_spotify()
# time.sleep(1.9)
# print(is_spotify_paused(get_access_token()))