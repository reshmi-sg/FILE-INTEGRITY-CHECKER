import hashlib
import os
import json

# === CONFIGURATION ===
MONITOR_FOLDER = "./monitor_folder"
HASH_RECORD_FILE = "file_hashes.json"
HASH_ALGO = "sha256"

def calculate_hash(file_path, algo="sha256"):
    """Calculate hash of a file using the given algorithm."""
    hash_func = getattr(hashlib, algo)()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        return None

def load_hashes(file_name):
    """Load previous file hashes from JSON file."""
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return {}

def save_hashes(hashes, file_name):
    """Save current file hashes to JSON file."""
    with open(file_name, "w") as f:
        json.dump(hashes, f, indent=4)

def get_all_files(folder):
    """Return a dictionary of relative file paths and their hashes."""
    file_hashes = {}
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder)
            file_hashes[rel_path] = calculate_hash(full_path, HASH_ALGO)
    return file_hashes

def compare_hashes(old, new):
    """Compare old and new hashes to detect changes."""
    all_keys = set(old.keys()) | set(new.keys())
    for file in all_keys:
        old_hash = old.get(file)
        new_hash = new.get(file)

        if old_hash is None:
            print(f"[NEW] File added: {file}")
        elif new_hash is None:
            print(f"[DELETED] File removed: {file}")
        elif old_hash != new_hash:
            print(f"[MODIFIED] File changed: {file}")
        else:
            print(f"[OK] No change: {file}")

def main():
    print("=== File Integrity Checker ===")
    print(f"Scanning folder: {MONITOR_FOLDER}\n")

    previous_hashes = load_hashes(HASH_RECORD_FILE)
    current_hashes = get_all_files(MONITOR_FOLDER)

    compare_hashes(previous_hashes, current_hashes)
    save_hashes(current_hashes, HASH_RECORD_FILE)

    print("\n✅ Integrity check complete.")

if __name__ == "__main__":
    main()
