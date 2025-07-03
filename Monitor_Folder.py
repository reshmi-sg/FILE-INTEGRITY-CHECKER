import os
import hashlib
import json
import time

HASH_DB = 'file_hashes.json'
MONITOR_FOLDER = './monitor_folder'  # Folder to monitor

def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def load_hashes():
    if not os.path.exists(HASH_DB):
        return {}
    with open(HASH_DB, 'r') as f:
        return json.load(f)

def save_hashes(hashes):
    with open(HASH_DB, 'w') as f:
        json.dump(hashes, f, indent=4)

def scan_files():
    file_hashes = {}
    for root, _, files in os.walk(MONITOR_FOLDER):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MONITOR_FOLDER)
            file_hashes[rel_path] = calculate_hash(full_path)
    return file_hashes

def check_for_changes(old_hashes, new_hashes):
    all_files = set(old_hashes) | set(new_hashes)
    for file in all_files:
        old = old_hashes.get(file)
        new = new_hashes.get(file)
        if old is None:
            print(f"[+] New file added: {file}")
        elif new is None:
            print(f"[-] File deleted: {file}")
        elif old != new:
            print(f"[!] File modified: {file}")

def monitor():
    print(f"Monitoring folder: {MONITOR_FOLDER}")
    old_hashes = load_hashes()
    new_hashes = scan_files()
    check_for_changes(old_hashes, new_hashes)
    save_hashes(new_hashes)

if __name__ == "__main__":
    while True:
        monitor()
        time.sleep(10)  # Re-scan every 10 seconds

