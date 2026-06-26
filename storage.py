import json
import os
import threading
class StorageEngine:
    def __init__(self, filepath="db_snapshot.json"):
        self.filepath = filepath
        self.data = {}
        self.lock = threading.Lock()
        self.load()
    def load(self):
        with self.lock:
            if os.path.exists(self.filepath):
                try:
                    with open(self.filepath, "r", encoding="utf-8") as f:
                        self.data = json.load(f)
                    print(f"[Storage] Loaded {len(self.data)} keys from '{self.filepath}'.")
                except Exception as e:
                    print(f"[Storage Error] Failed to load snapshot '{self.filepath}': {e}")
                    print("[Storage] Starting with an empty database.")
                    self.data = {}
            else:
                print(f"[Storage] No snapshot found at '{self.filepath}'. Starting empty.")
                self.data = {}
    def save(self):
        with self.lock:
            temp_filepath = self.filepath + ".tmp"
            try:
                with open(temp_filepath, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4)
                if os.path.exists(self.filepath):
                    os.remove(self.filepath)
                os.rename(temp_filepath, self.filepath)
            except Exception as e:
                print(f"[Storage Error] Failed to write snapshot: {e}")
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
    def get(self, key):
        with self.lock:
            return self.data.get(key)
    def set(self, key, value):
        with self.lock:
            self.data[key] = value
        self.save()
        return True
    def delete(self, key):
        existed = False
        with self.lock:
            if key in self.data:
                del self.data[key]
                existed = True
        if existed:
            self.save()
        return existed
    def list_keys(self):
        with self.lock:
            return list(self.data.keys())
