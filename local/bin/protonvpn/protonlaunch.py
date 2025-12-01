#!/usr/bin/env python3
import sys
import subprocess


def run(cmd):
    return subprocess.run(
        cmd, shell=True, text=True, capture_output=True, executable="/bin/bash"
    )


def toggle_ipv6_disable(val: int):
    subprocess.run(
        f"sudo sysctl -w net.ipv6.conf.all.disable_ipv6={val} "
        f"net.ipv6.conf.default.disable_ipv6={val}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def active_interfaces():
    result = run("wg show interfaces")
    return result.stdout.strip().split() if result.returncode == 0 else []


def main():
    current = active_interfaces()
    if current:
        print(f"Disconnecting: {' '.join(current)}")
        run(f"sudo wg-quick down {' '.join(current)}")
        toggle_ipv6_disable(0)
    if len(sys.argv) == 2:
        server = sys.argv[1]
        print(f"Connecting → {server}")
        toggle_ipv6_disable(1)
        result = run(f"sudo wg-quick up {server}")
        if result.returncode != 0:
            print("Failed to connect")
            toggle_ipv6_disable(0)
            sys.exit(1)
        print(f"Connected → {' '.join(active_interfaces())}")


if __name__ == "__main__":
    main()

