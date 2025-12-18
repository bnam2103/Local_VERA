# main.py
from ASR import record_audio, record_until_silence, transcribe, transcribe_long
from LLM import VeraAI
from TTS import speak
import torch
import string
import time
from intent import is_command
from action_dispatcher import decision_tree
from voice_detection import record_on_voice
from actions.check_time import is_time_or_date_query
# ------------------------------
# CONFIG
# ------------------------------

VERA_MODEL_PATH = r"C:\Users\User\Documents\Fine_Tuning_Projects\LLAMA_LLM_3B"

# Initialize VERA
vera = VeraAI(VERA_MODEL_PATH)

print("=== VERA Voice Assistant ===")
print("Press Ctrl+C or say 'exit' to quit.\n")

greeting = vera.ask("Hi")
print(f"VERA: {greeting}\n")
speak(greeting)

try:
    while True:
        # Step 1: Record audio from user
        audio = record_on_voice()
        
        # Step 2: Transcribe speech to text
        print(" Transcribing...")
        user_text = transcribe_long(audio)
        # Skip empty inputs
        if user_text.strip() == "":
            continue
        # can't transcribe "laufey" properly, so replace it    
        user_text = user_text.replace("my favorite artist", "laufey")    
        print(f"You said: {user_text}\n")

        # Step 3: Classify intent (command)
        if is_command(user_text):
            # Step 3.1.1: Send Text to VERA LLM for command handling
            print("VERA executing command...")
            vera_reply = vera.ask(user_text)
            print(f"VERA: {vera_reply}\n")
            # Step 3.1.2: Speak the response and perform action
            speak(vera_reply)
            decision_tree(user_text)
            # time.sleep(1)
            continue

        # Step 3.2: Send text to VERA LLM for general response (non-command)
        vera_reply = vera.ask(user_text)
        if is_time_or_date_query(vera_reply):
            # Skip printing and speaking VERA's response
            decision_tree(vera_reply)

        else:
            # Normal behavior
            print("VERA thinking...")
            vera_reply = vera.ask(user_text)
            print(f"VERA: {vera_reply}\n")
            # time.sleep(0.1)
            speak(vera_reply)
            # decision_tree(vera_reply) # this could be good follow up but bad at the same time
        # time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting. Goodbye!")
