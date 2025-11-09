#!/usr/bin/env python3
import os
import socket
import subprocess
import time

import imaplib2

SCRIPT_DIR = os.path.expanduser("~/.ssh")
CREDENTIAL_FILE = os.path.join(SCRIPT_DIR, "bridge_creds.txt")
LAST_SUBJECT_FILE = os.path.expanduser("~/.cache/last_email_subject.txt")

# --- Load credentials ---
creds = {}
try:
    with open(CREDENTIAL_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line:
                key, value = line.split("=", 1)
                creds[key.strip()] = value.strip()
except FileNotFoundError:
    raise FileNotFoundError(f"Credential file not found: {CREDENTIAL_FILE}")

IMAP_HOST = creds.get("IMAP_HOST")
IMAP_PORT = int(creds.get("IMAP_PORT", "0"))
USERNAME = creds.get("USERNAME")
PASSWORD = creds.get("PASSWORD")

if not all([IMAP_HOST, IMAP_PORT, USERNAME, PASSWORD]):
    raise ValueError("Missing ProtonMail Bridge credentials in bridge_creds.txt")

# --- Load last subject ---
old_subject = ""
if os.path.exists(LAST_SUBJECT_FILE):
    with open(LAST_SUBJECT_FILE, "r") as f:
        old_subject = f.read().strip()

# --- Start ProtonMail Bridge ---
bridge_proc = subprocess.Popen(["protonmail-bridge", "--no-window"])
print("Starting ProtonMail Bridge...")

# Wait for IMAP port to open
for _ in range(60):
    try:
        with socket.create_connection((IMAP_HOST, IMAP_PORT), timeout=2):
            print("Bridge IMAP port is open.")
            break
    except (ConnectionRefusedError, socket.timeout):
        time.sleep(1)
else:
    raise TimeoutError("ProtonMail Bridge IMAP port did not open in time.")

# --- Connect and login with retry ---
imap = imaplib2.IMAP4(IMAP_HOST, IMAP_PORT)
imap.starttls()
imap.capability()   # <-- critical for ProtonMail Bridge v3
imap.login(USERNAME, PASSWORD)
for attempt in range(30):
    time.sleep(2)
    try:
        imap = imaplib2.IMAP4(IMAP_HOST, IMAP_PORT)
        imap.login(USERNAME, PASSWORD)
        print("Logged in successfully.")
        break
    except imaplib2.IMAP4.error as e:
        msg = str(e)
        if "no such user" in msg.lower() or "authentication failed" in msg.lower():
            print("Bridge not ready yet, retrying login...")
            continue
        else:
            raise
else:
    raise RuntimeError("Failed to login after multiple attempts.")

try:
    imap.select("INBOX")
    status, data = imap.search(None, "ALL")
    if status != "OK":
        raise RuntimeError("Failed to search mailbox")

    email_ids = data[0].split()
    if email_ids:
        last_email_id = email_ids[-1]
        status, msg_data = imap.fetch(
            last_email_id, "(BODY[HEADER.FIELDS (SUBJECT FROM)])"
        )
        if status == "OK":
            header_text = msg_data[0][1].decode("utf-8", errors="replace")

            subject = ""
            for line in header_text.splitlines():
                if line.lower().startswith("subject:"):
                    subject = line[len("Subject:") :].strip()
                    break

            if subject and subject != old_subject:
                subprocess.run(["notify-send", "ProtonMail", subject])
                with open(LAST_SUBJECT_FILE, "w") as f:
                    f.write(subject)

    imap.logout()
    print("Logged out successfully.")

finally:
    if bridge_proc.poll() is None:
        print("Stopping ProtonMail Bridge...")
        bridge_proc.terminate()
        try:
            bridge_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bridge_proc.kill()
