from timer.lib.create_timer import create_timer
from lib.list_timers import list_timers
from lib.check_status import check_timer_status


def main():
    while True:
        print("""
====================================
🕒 Systemd Timer Helper (Guided Mode)
====================================
1) Create a new timer
2) List my timers
3) Check a timer status
4) Exit
""")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            create_timer()
        elif choice == "2":
            list_timers()
        elif choice == "3":
            check_timer_status()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
