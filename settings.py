import json

SETTINGS_FILE = "settings.json"

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)
