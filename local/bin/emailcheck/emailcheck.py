#!/usr/bin/env python3
import imaplib2
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path.home() / ".ssh"
CREDENTIAL_FILE = SCRIPT_DIR / "bridge_creds.txt"
LAST_SUBJECT_FILE = Path.home() / ".cache" / "last_email_subject.txt"
SLEEP_TIME = 30


def load_credentials(file_path):
    creds = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line:
                key, value = line.split("=", 1)
                creds[key.strip()] = value.strip()
    required_keys = ["IMAP_HOST", "IMAP_PORT", "USERNAME", "PASSWORD"]
    if not all(k in creds for k in required_keys):
        raise ValueError("Missing ProtonMail Bridge credentials in bridge_creds.txt")
    return creds


def read_last_subject():
    try:
        with open(LAST_SUBJECT_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def write_last_subject(subject):
    LAST_SUBJECT_FILE.mkdir(parents=True, exist_ok=True)
    with open(LAST_SUBJECT_FILE, "w") as f:
        f.write(subject)


def start_bridge_service():
    subprocess.run(["systemctl", "--user", "start", "protonmail-bridge.service"])
    print(
        f"Starting ProtonMail Bridge... waiting {SLEEP_TIME} seconds for it to initialize"
    )
    time.sleep(SLEEP_TIME)


def stop_bridge_service():
    print("Stopping ProtonMail Bridge service...")
    subprocess.run(["systemctl", "--user", "stop", "protonmail-bridge.service"])


def fetch_last_email_subject(imap_host, imap_port, username, password):
    imap = imaplib2.IMAP4(imap_host, int(imap_port))
    imap.login(username, password)
    imap.select("INBOX")
    status, data = imap.search(None, "ALL")
    email_ids = data[0].split()
    subject = ""
    if email_ids:
        last_email_id = email_ids[-1]
        status, msg_data = imap.fetch(
            last_email_id, "(BODY[HEADER.FIELDS (SUBJECT FROM)])"
        )
        header_text = msg_data[0][1].decode()
        for line in header_text.splitlines():
            if line.startswith("Subject:"):
                subject = line[len("Subject:") :].strip()
                break
    imap.logout()
    return subject


def send_notification(subject):
    subprocess.run(["notify-send", "ProtonMail", subject])


def main():
    creds = load_credentials(CREDENTIAL_FILE)
    old_subject = read_last_subject()
    start_bridge_service()
    try:
        subject = fetch_last_email_subject(
            creds["IMAP_HOST"], creds["IMAP_PORT"], creds["USERNAME"], creds["PASSWORD"]
        )
        if subject and subject != old_subject:
            send_notification(subject)
            write_last_subject(subject)
    finally:
        stop_bridge_service()


if __name__ == "__main__":
    main()
