import sys
from ASR import transcribe   
from TTS import speak
import re
import threading
import queue
import numpy as np
import time
import string
# -------------------------
# Helper functions
# -------------------------
import threading
import numpy as np
import queue
import sounddevice as sd
from actions.chrome import open_chrome, close_chrome, check_weather, search_google
from actions.spotify import open_spotify, close_spotify, get_spotify_track_uri, get_access_token, play_spotify_song, pause_spotify, increase_volume, decrease_volume, mute
from actions.check_time import check_time, check_date

audio_queue = queue.Queue()

def record_thread(stop_event):
    """Continuously record chunks until stop_event is set."""
    while not stop_event.is_set():
        audio = record_audio(duration=1.5)
        audio_queue.put(audio)

def record_audio(duration=1.5, sample_rate=16000):
    """Record audio and release stream immediately."""
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()  
    return audio.squeeze()

audio_queue = queue.Queue()

def heard_wake_word(text):
    # lowercase
    text = text.lower().strip()

    # remove punctuation except spaces
    text = re.sub(r"[^\w\s]", " ", text)

    # collapse multiple spaces into one
    text = re.sub(r"\s+", " ", text)

    # split text into words
    words = text.split()

    # check for "hey vera" first
    if "hey" in words and "vera" in words:
        return True

    # check for "hey" alone as a wake word
    if "hey" in words:
        return True

    return False

# -------------------------
# Main action functions
# -------------------------
def exit_program():
    print("Exiting program. Goodbye!")
    sys.exit(0)

def pause():
    print("Pausing... Say 'hey vera' to resume.")
    
    stop_event = threading.Event()
    t = threading.Thread(target=record_thread, args=(stop_event,), daemon=True)
    t.start()

    accumulated_audio = np.array([], dtype=np.float32)

    while True:
        try:
            chunk = audio_queue.get(timeout=5)
        except queue.Empty:
            continue

        accumulated_audio = np.concatenate([accumulated_audio, chunk])

        if len(accumulated_audio) >= 2 * 16000:
            text = transcribe(accumulated_audio)
            # print(f"Heard: {text}")  # debugging

            if heard_wake_word(text):
                print(" Resuming...")
                break

            accumulated_audio = np.array([], dtype=np.float32)

    # Stop the recording thread and release audio device
    stop_event.set()
    t.join()
    sd.stop()  # ensure sounddevice streams are released
    # Tiny delay to let TTS acquire audio output
    time.sleep(0.1)

# -------------------------
# Decision tree
# -------------------------
def decision_tree(intent):
    intent = intent.lower()
    intent = intent.translate(str.maketrans("", "", string.punctuation))
    if  any(keyword in intent for keyword in ["exit", "shut down", "quit"]):
        for keyword in ["exit", "shut down", "quit"]:
            if keyword in intent:
                exit_program()
                break
    # elif "open Chrome" in intent:
    #     open_chrome()
    elif any(keyword in intent for keyword in ["close chrome", "closing chrome"]):
        for keyword in ["close chrome", "closing chrome"]:
            if keyword in intent:
                close_chrome()
                break
    elif any(keyword in intent for keyword in ["open spotify", "opening spotify"]):
        for keyword in ["open spotify", "opening spotify"]:
            if keyword in intent:
                open_spotify()
                break
    elif any(keyword in intent for keyword in ["close spotify", "closing spotify"]):
        for keyword in ["close spotify", "closing spotify"]:
            if keyword in intent:
                close_spotify()
                break
    # elif "check the weather" in intent:
    #     weather_info = check_weather()
    #     if weather_info:
    #         speak(weather_info)
    elif any(keyword in intent for keyword in ["what time is it", "current time", "check the time"]):
        current_time = check_time()
        speak(current_time)

    elif any(keyword in intent for keyword in ["what date is it", "current date", "check date", "today's date"]):
        current_date = check_date()
        speak(current_date)

    elif any(keyword in intent for keyword in ["search", "search up", "searching","look up"]):
        for keyword in [ "search up", "searching","look up","search"]:  
            if keyword in intent:
                idx = intent.find(keyword)
                query = intent[idx + len(keyword):].strip()
                query = query.translate(str.maketrans("", "", string.punctuation))
                break
        if query:
            search_google(query)
        else:
            print("No search query provided.")
    elif any(keyword in intent for keyword in ["play"]):
        # Example: "Play Blinding Lights by The Weeknd"
        access_token = get_access_token()
        try:
            if " by " in intent:
                after_play = intent.lower().split("play", 1)[1].strip()  # split only once
                parts = after_play.split(" by ", 1)  # split into song and artist
                song_name = parts[0].replace("play song", "").replace("play", "").strip()
                artist_name = parts[1].strip()
            else:
                print("Please specify the song and artist in the format: 'play [song] by [artist]'")
                return
        except Exception as e:
            print("Error parsing song and artist:", e)
            return

        track_uri = get_spotify_track_uri(song_name, artist_name, access_token)
        if track_uri:
            open_spotify()
            # time.sleep(1)  # wait for Spotify to open
            # pause_spotify()  # ensure Spotify is ready
            # time.sleep(0.5)  # brief pause
            play_spotify_song(track_uri)
        else:
            print(f"Could not find track '{song_name}' by '{artist_name}'.")
    elif any(keyword in intent for keyword in ["pause spotify", "pause the music", "pause the song", "unpause the music","unpause the song", "unpause spotify"]):
        for keyword in ["pause spotify", "pause the music", "pause the song", "unpause the music","unpause the song", "unpause spotify"]:
            if keyword in intent:
                open_spotify()
                time.sleep(1)
                pause_spotify()
                break
    elif any(keyword in intent for keyword in ["turn up", "increase volume"]):
        for keyword in ["turn up", "increase volume"]:
            if keyword in intent:
                increase_volume()
                break
    elif any(keyword in intent for keyword in ["turn down", "decrease volume"]):
        for keyword in ["turn down", "decrease volume"]:
            if keyword in intent:
                decrease_volume()
                break
    elif any(keyword in intent for keyword in ["turn off the audio", "mute","unmute","turn on the audio"]):
        for keyword in ["unmute", "mute"]:
            if keyword in intent:
                mute()
                break             
    elif "pause" in intent:
        pause()
        speak("Hi, I'm back.")
    else:
        print("Action not recognized.")

# -------------------------
# Test / Example usage
# -------------------------

# decision_tree("Can you play Blinding Lights by The Weeknd")