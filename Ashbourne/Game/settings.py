import json
import os

SAVE_DIR = os.path.join(os.path.dirname(__file__), "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


class Settings:
    def __init__(self):
        self.language = "en"
        self.brightness = 1.0
        self._load()

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                self.language = data.get("language", "en")
                self.brightness = data.get("brightness", 1.0)
            except Exception:
                pass

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({"language": self.language, "brightness": self.brightness}, f)
        except Exception:
            pass

    def set_language(self, lang):
        self.language = lang
        self.save()

    def set_brightness(self, val):
        self.brightness = max(0.3, min(1.5, val))
        self.save()


class SaveManager:
    def __init__(self):
        os.makedirs(SAVE_DIR, exist_ok=True)

    def save(self, game_state):
        """Save the game state to disk.
        game_state: dict with player, progress, quests, killed, used, map_id, player_pos
        """
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(game_state, f)
            return True
        except Exception:
            return False

    def load(self):
        """Load game state from disk. Returns dict or None."""
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            return data
        except Exception:
            return None

    def has_save(self):
        return os.path.exists(SAVE_FILE)

    def delete(self):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
