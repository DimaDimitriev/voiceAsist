import json
import os
import sys

import queue

import pyttsx3
import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel

import config

SAMPLE_RATE = 16000
SetLogLevel(-1)  # без служебного шума Vosk в консоли

if not os.path.isdir(config.VOSK_MODEL_PATH):
    sys.exit(
        f"Не найдена модель Vosk: {config.VOSK_MODEL_PATH}\n"
        "Скачайте vosk-model-small-ru с https://alphacephei.com/vosk/models "
        "и распакуйте в папку проекта."
    )

model = Model(config.VOSK_MODEL_PATH)


def _russian_voice_id(engine):
    """Ищет русский голос; если его нет, вернёт None и останется голос по умолчанию."""
    for v in engine.getProperty("voices"):
        info = f"{v.id} {v.name}".lower()
        if "ru-ru" in info or "russian" in info or "_ru_" in info:
            return v.id
    return None


def speak(text: str):
    """Озвучка: движок создаётся заново на каждую фразу — так pyttsx3 не зависает на Windows."""
    print(f"Ассистент: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 190)
        voice_id = _russian_voice_id(engine)
        if voice_id:
            engine.setProperty("voice", voice_id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[!] Ошибка озвучки: {e}")


def listen() -> str:
    """Открывает микрофон, ждёт непустую фразу и всегда закрывает микрофон."""
    audio_queue: "queue.Queue[bytes]" = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        audio_queue.put(bytes(indata))

    rec = KaldiRecognizer(model, SAMPLE_RATE)
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype="int16",
                           channels=1, callback=on_audio):
        print(">>> Слушаю...")
        while True:
            if rec.AcceptWaveform(audio_queue.get()):
                text = json.loads(rec.Result()).get("text", "").strip()
                if text:
                    return text