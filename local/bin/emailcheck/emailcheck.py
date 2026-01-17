#!/usr/bin/env python3
import os
import imaplib2
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path.home() / ".ssh"
CREDENTIAL_FILE = SCRIPT_DIR / "bridge_creds.txt"
LAST_SUBJECT_FILE = Path.home() / ".cache" / "last_email_subject.txt"
SLEEP_TIME = 30


def zenity_prompt(title, text, hide=False):
    cmd = [
        "zenity",
        "--entry",
        f"--title={title}",
        f"--text={text}",
    ]
    if hide:
        cmd.append("--hide-text")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("User cancelled credential entry")
    return result.stdout.strip()


def create_credentials_file():
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    creds = {
        "IMAP_HOST": zenity_prompt("ProtonMail Bridge", "Enter IMAP host:"),
        "IMAP_PORT": zenity_prompt("ProtonMail Bridge", "Enter IMAP port:"),
        "USERNAME": zenity_prompt("ProtonMail Bridge", "Enter username:"),
        "PASSWORD": zenity_prompt("ProtonMail Bridge", "Enter password:", hide=True),
    }
    with open(CREDENTIAL_FILE, "w") as f:
        for k, v in creds.items():
            f.write(f"{k}={v}\n")
    os.chmod(CREDENTIAL_FILE, 0o600)  # secure permissions


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
    if not CREDENTIAL_FILE.exists():
        create_credentials_file()  # prompts via Zenity and saves creds
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
