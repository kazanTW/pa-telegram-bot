import json
import os

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        print("data.json does not exist or empty, intitalizing...")
        save_data({"notes": [], "reminder_time": None, "chat_id": None})

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecoderError:
            print("data.json is broken, initializing...")
            save_data({"notes": [], "reminder_time": None, "chat_id": None})
            return {"notes": [], "reminder_time": None, "chat_id": None}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
