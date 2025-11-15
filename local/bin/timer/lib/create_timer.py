from utils import run, load_registry, save_registry, SYSTEMD_USER_DIR


def write_unit_files(timer_name, command, interval):
    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)

    service_file = SYSTEMD_USER_DIR / f"{timer_name}.service"
    timer_file = SYSTEMD_USER_DIR / f"{timer_name}.timer"

    service_file.write_text(f"""[Unit]
Description=Service for {timer_name}  # managed by my_timer_helper

[Service]
Type=oneshot
ExecStart={command}
""")

    timer_file.write_text(f"""[Unit]
Description=Timer for {timer_name}  # managed by my_timer_helper

[Timer]
OnUnitActiveSec={interval}
Unit={timer_name}.service

[Install]
WantedBy=timers.target
""")


def create_timer():
    print("\n🛠️ Create a new systemd timer")
    timer_name = input("Give this timer a name (no spaces): ").strip()

    command = input("Enter the command to run (default: notification): ").strip()
    if not command:
        command = f"notify-send -u critical '{timer_name} triggered!'"

    interval = input("How often should it run? (e.g. 30min, 1h, daily): ").strip()
    write_unit_files(timer_name, command, interval)

    run("systemctl --user daemon-reload")
    out, err, code = run(f"systemctl --user enable --now {timer_name}.timer")

    if code != 0:
        print(f"❌ Failed to start timer: {err}")
        return

    registry = load_registry()
    registry[timer_name] = {"command": command, "interval": interval}
    save_registry(registry)

    print(f"\n✔️ Timer '{timer_name}' created and running every {interval}.\n")
