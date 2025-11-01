#!/usr/bin/env python3
import imaplib2
import os
import subprocess
import time

SCRIPT_DIR = os.path.expanduser("~/.ssh")
CREDENTIAL_FILE = os.path.join(SCRIPT_DIR, "bridge_creds.txt")
creds = {}
with open(CREDENTIAL_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if line and "=" in line:
            key, value = line.split("=", 1)
            creds[key.strip()] = value.strip()

IMAP_HOST = creds.get("IMAP_HOST", "")
IMAP_PORT = int(creds.get("IMAP_PORT", 0))
USERNAME = creds.get("USERNAME", "")
PASSWORD = creds.get("PASSWORD", "")

if not all([IMAP_HOST, IMAP_PORT, USERNAME, PASSWORD]):
    raise ValueError("Missing ProtonMail Bridge credentials in bridge_creds.txt")

LAST_SUBJECT_FILE = os.path.expanduser("~/.cache/last_email_subject.txt")

try:
    with open(LAST_SUBJECT_FILE, "r") as f:
        old_subject = f.read().strip()
except FileNotFoundError:
    old_subject = ""

bridge_proc = subprocess.Popen(["protonmail-bridge", "--no-window"])
print("Starting ProtonMail Bridge... waiting 30 seconds for it to initialize")
time.sleep(30)

try:
    imap = imaplib2.IMAP4(IMAP_HOST, IMAP_PORT)
    imap.login(USERNAME, PASSWORD)
    imap.select("INBOX")

    status, data = imap.search(None, "ALL")
    email_ids = data[0].split()

    if email_ids:
        last_email_id = email_ids[-1]
        status, msg_data = imap.fetch(last_email_id, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
        header_text = msg_data[0][1].decode()

        subject = ""
        for line in header_text.splitlines():
            if line.startswith("Subject:"):
                subject = line[len("Subject:"):].strip()
                break

        if subject and subject != old_subject:
            subprocess.run(["notify-send", "ProtonMail", subject])
            with open(LAST_SUBJECT_FILE, "w") as f:
                f.write(subject)

    imap.logout()

finally:
    if 'bridge_proc' in locals() and bridge_proc:
        print("Stopping ProtonMail Bridge...")
        bridge_proc.terminate()
        try:
            bridge_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bridge_proc.kill()
