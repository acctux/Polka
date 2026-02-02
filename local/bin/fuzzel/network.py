import subprocess
import os
import sys

# Define choices
CHOICE_1 = "WiFi"
CHOICE_2 = "VPN"
CANCEL = "Cancel"


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


# Function to display the menu using Fuzzel
def display_menu(menu, lines):
    try:
        choice = subprocess.run(
            [
                "fuzzel",
                "--dmenu",
                "--hide-prompt",
                "--lines",
                str(lines),
                "--config",
                os.path.expanduser("~/.config/fuzzel/vpnmenu.ini"),
            ],
            input=menu,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return choice
    except subprocess.CalledProcessError:
        return ""


def wifi_choice():
    subprocess.run(
        [sys.executable, os.path.expanduser("~/.local/bin/network/network.py")]
    )


def vpn_choice():
    list_path = "/run/wireguard/connections.list"
    if os.path.exists(list_path):
        with open(list_path, "r") as f:
            vpns = f.read().strip()
        lines = len(vpns.splitlines())
        vpns = "Disconnect\n" + vpns
        choice = display_menu(vpns, lines + 1)  # +1 for "Disconnect"
        if not choice:
            sys.exit(1)
        if choice == "Back":
            return
        elif choice == "Disconnect":
            subprocess.run(
                [
                    "sudo",
                    "-A",
                    os.path.expanduser("~/.local/bin/protonvpn/protonconnect.py"),
                ]
            )
        else:
            subprocess.run(
                [
                    "sudo",
                    "-A",
                    os.path.expanduser("~/.local/bin/protonvpn/protonconnect.py"),
                    choice,
                ]
            )
    else:
        print(f"VPN connections list {list_path} not found!")
        sys.exit(1)


def main():
    while True:
        menu = f"{CHOICE_1}\n{CHOICE_2}\n{CANCEL}"
        choice = display_menu(menu, 3)
        if choice == CHOICE_1:
            wifi_choice()
            break
        elif choice == CHOICE_2:
            vpn_choice()
            break
        elif choice == CANCEL or choice == "":
            sys.exit(0)


if __name__ == "__main__":
    main()

