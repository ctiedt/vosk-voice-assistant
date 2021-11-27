#!/usr/bin/env python3

import queue
import sounddevice as sd
import vosk
import sys
import json
import requests
import pyttsx3
import random
import configparser

API_URL = None
TOKEN = None

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def handle_input(text: str, engine):
    print(text)
    text = text.strip().lower()
    if "mach clemens lampe an" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_on",
                            data='{"entity_id": "light.clemens_lampe"}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "mach clemens lampe aus" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_off",
                            data='{"entity_id": "light.clemens_lampe"}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "mach ronja lampe an" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_on",
                            data='{"entity_id": "light.ronjas_lampe"}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "mach ronja lampe aus" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_off",
                            data='{"entity_id": "light.ronjas_lampe"}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "mach das licht an" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_on",
                            data='{"entity_id": ["light.clemens_lampe", "light.ronjas_lampe"]}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "mach das licht aus" in text:
        res = requests.post(f"{API_URL}/api/services/light/turn_off",
                            data='{"entity_id": ["light.clemens_lampe", "light.ronjas_lampe"]}', headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code >= 200 and res.status_code <= 300:
            engine.say("Okeh.")
            engine.runAndWait()
    if "singe mir ein lied" in text:
        engine.say("la la la.")
        engine.runAndWait()
    if "wirf einen würfel" in text:
        die = random.randint(1, 6)
        engine.say(f"Das Ergebnis ist {die}")
        engine.runAndWait()


def main():
    global API_URL
    global TOKEN
    config = configparser.ConfigParser()
    config.read("config.ini")
    API_URL = config["HomeAssistant"]["API_URL"]
    TOKEN = config["HomeAssistant"]["TOKEN"]
    engine = pyttsx3.init()
    try:
        device_info = sd.query_devices(None, 'input')
        print(device_info)
        samplerate = int(device_info['default_samplerate'])

        model = vosk.Model("model")

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result())["text"]
                    handle_input(text, engine)
                else:
                    res = rec.PartialResult()
                    print(f'Partial: {json.loads(res)["partial"]}')

    except KeyboardInterrupt:
        print('\nDone')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
