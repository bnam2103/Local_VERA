import numpy as np
import sounddevice as sd
from collections import deque
from ASR import record_until_silence, transcribe_long
import time
import torch
CHUNK_DURATION = 0.05  # 100ms per chunk
SAMPLE_RATE = 16000
THRESHOLD = 0.05 # increase this value if there are people around (0.03 when alone; 0.1 when people are around)
PRE_BUFFER_CHUNKS = 10000  # For full pre-buffering

# def wait_for_voice():
#     print("Waiting for your voice...")
    
#     # small buffer to store audio before threshold
#     pre_buffer = deque(maxlen=PRE_BUFFER_CHUNKS)
    
#     while True:
#         audio_chunk = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
#         sd.wait()
        
#         pre_buffer.append(audio_chunk.copy())
        
#         if np.max(np.abs(audio_chunk)) > THRESHOLD:
#             print("Voice detected!")
            
#             # concatenate pre-buffer to include first words
#             full_audio = np.concatenate(list(pre_buffer))
#             return full_audio

def load_silero_vad_torch():
    vad_model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False
    )
    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    return vad_model, get_speech_timestamps, VADIterator

vad_model, get_speech_timestamps, VADIterator = load_silero_vad_torch()
vad_iterator = VADIterator(vad_model)       


# def record_on_voice(
#     sample_rate=16000,
#     chunk_ms=20,
#     silence_time=1.35,
#     vad_threshold=0.35,
#     preroll_ms=200
# ):
#     chunk_size = int(sample_rate * chunk_ms / 1000)
#     silent_chunks_needed = int(silence_time * 1000 / chunk_ms)
#     preroll_chunks = int(preroll_ms / chunk_ms)

#     preroll = deque(maxlen=preroll_chunks)
#     audio_buffer = []
#     vad_buffer = torch.zeros(0)

#     silent_count = 0
#     speech_started = False

#     vad_iterator.reset_states()

#     print("Waiting for your voice...")

#     with sd.InputStream(
#         samplerate=sample_rate,
#         channels=1,
#         dtype="float32",
#         blocksize=chunk_size,
#     ) as stream:

#         while True:
#             chunk, _ = stream.read(chunk_size)
#             chunk = chunk.squeeze()

#             preroll.append(chunk.copy())
#             vad_buffer = torch.cat([vad_buffer, torch.tensor(chunk)])

#             if vad_buffer.numel() < 512:
#                 continue

#             speech_prob = vad_model(vad_buffer[-512:], sample_rate).item()

#             # ---- SPEECH START ----
#             if not speech_started and speech_prob > vad_threshold:
#                 print("Voice detected!")
#                 speech_started = True
#                 audio_buffer.extend(preroll)
#                 silent_count = 0

#             # ---- RECORDING ----
#             if speech_started:
#                 audio_buffer.append(chunk.copy())

#                 if speech_prob < vad_threshold:
#                     silent_count += 1
#                 else:
#                     silent_count = 0

#                 if silent_count >= silent_chunks_needed:
#                     break

#     return np.concatenate(audio_buffer).astype("float32")


### New implementation with loudness check###
def rms_db(chunk, eps=1e-8):
    rms = np.sqrt(np.mean(chunk ** 2))
    return 20 * np.log10(rms + eps)

def record_on_voice(
    sample_rate=16000,
    chunk_ms=20,
    silence_time=1.35,
    start_threshold=0.35,
    stop_threshold=0.20,
    preroll_ms=200,
    loudness_db_threshold=-40
):
    chunk_size = int(sample_rate * chunk_ms / 1000)
    silent_chunks_needed = int(silence_time * 1000 / chunk_ms)
    preroll_chunks = int(preroll_ms / chunk_ms)

    preroll = deque(maxlen=preroll_chunks)
    audio_buffer = []
    vad_buffer = torch.zeros(0)

    silent_count = 0
    speech_started = False
    speech_count = 0
    START_FRAMES = 3

    vad_iterator.reset_states()

    print("Waiting for your voice...")

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        blocksize=chunk_size,
    ) as stream:

        while True:
            chunk, _ = stream.read(chunk_size)
            chunk = chunk.squeeze()

            preroll.append(chunk.copy())
            vad_buffer = torch.cat([vad_buffer, torch.tensor(chunk)])

            if vad_buffer.numel() < 512:
                continue

            speech_prob = vad_model(vad_buffer[-512:], sample_rate).item()
            db = rms_db(chunk)

            # ---------- SPEECH START ----------
            if not speech_started:
                if speech_prob > start_threshold and db > loudness_db_threshold:
                    speech_count += 1
                    if speech_count >= START_FRAMES:
                        speech_started = True
                        audio_buffer.extend(preroll)
                        silent_count = 0
                        print("Voice detected!")
                else:
                    speech_count = 0

            # ---------- RECORDING ----------
            if speech_started:
                audio_buffer.append(chunk.copy())

                if speech_prob < stop_threshold:
                    silent_count += 1
                else:
                    silent_count = 0

                if silent_count >= silent_chunks_needed:
                    break

    return np.concatenate(audio_buffer).astype("float32")

##################################
# Example usage
##################################
# while True:
#     wait_for_voice()
#     print("Please speak after the prompt...")
#     audio = record_until_silence()
        
#     print(" Transcribing...")
#     user_text = transcribe_long(audio)
#     print(f"You said: {user_text}\n")


# while True:
#     audio = record_on_voice()
#     print("Transcribing...")
#     text = transcribe_long(audio)
#     print(f"You said: {text}\n")