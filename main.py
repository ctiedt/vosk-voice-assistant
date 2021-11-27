#!/usr/bin/env python3

import queue
from typing import Callable
import sounddevice as sd
import vosk
import sys
import json
import requests
import random
import configparser

from assistant import Assistant
from command import Command, CommandError

API_URL = None
TOKEN = None

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def api_request(path: str, data: str) -> Callable:
    def func():
        res = requests.post(f"{API_URL}{path}",
                            data=str(data), headers={"Authorization": f"Bearer {TOKEN}"})
        if res.status_code < 200 or res.status_code >= 300:
            raise CommandError
    return func


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


def roll_d6():
    die = random.randint(1, 6)
    return f"Das Ergebnis ist {die}"


def phrases():
    """Returns recognized phrases until `KeyboardInterrupt` """
    device_info = sd.query_devices(None, 'input')
    print(device_info)
    samplerate = int(device_info['default_samplerate'])

    model = vosk.Model("model")

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result())["text"]
                    # handle_input(text, engine)
                    yield text
                else:
                    res = rec.PartialResult()
                    print(f'Partial: {json.loads(res)["partial"]}')
        except KeyboardInterrupt:
            print("Done")


def main():
    global API_URL
    global TOKEN
    config = configparser.ConfigParser()
    config.read("config.ini")
    API_URL = config["HomeAssistant"]["API_URL"]
    TOKEN = config["HomeAssistant"]["TOKEN"]

    assistant = Assistant()
    assistant.add_command(Command("mach clemens lampe an", api_request(
        "/api/services/light/turn_on", '{"entity_id": "light.clemens_lampe"}')))
    assistant.add_command(Command("mach clemens lampe aus", api_request(
        "/api/services/light/turn_off", '{"entity_id": "light.clemens_lampe"}')))
    assistant.add_command(Command("wirf einen würfel", roll_d6))
    assistant.add_command(Command("singe mir ein lied", lambda: "la la la"))

    assistant.run(phrases())


if __name__ == "__main__":
    main()
