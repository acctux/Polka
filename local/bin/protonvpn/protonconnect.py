#!/usr/bin/env python3
import asyncio
import sys
from concurrent.futures import Future

from proton.vpn.app.gtk.controller import Controller
from proton.vpn.app.gtk.utils.executor import AsyncExecutor
from proton.vpn.app.gtk.utils.exception_handler import ExceptionHandler


class DummyExceptionHandler(ExceptionHandler):
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        print("Error:", exc_value, file=sys.stderr)


async def run_blocking_future(fut: Future):
    """Helper to properly await a concurrent.futures.Future in asyncio"""
    while not fut.done():
        await asyncio.sleep(0.1)
    return fut.result()


async def main():
    executor = AsyncExecutor()
    exception_handler = DummyExceptionHandler()

    print("Initializing Proton VPN controller (10–20s first time)...")
    controller = Controller(executor=executor, exception_handler=exception_handler)

    # This is the CORRECT way: submit + wait via our helper
    init_future: Future = executor.submit(controller.initialize_vpn_connector)
    await run_blocking_future(init_future)

    print("Controller initialized!")

    # Reuse existing login if possible
    if controller.user_logged_in:
        print("Already logged in")
    else:
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        login_future = controller.login(username, password)
        await run_blocking_future(login_future)

        if not controller.user_logged_in:
            exc = login_future.exception()
            if exc and "two factor" in str(exc).lower():
                code = input("2FA code: ").strip()
                await run_blocking_future(controller.submit_2fa_code(code))
            else:
                print("Login failed:", exc)
                return

        print("Logged in!")

    # Status updates
    def on_status(state):
        desc = getattr(state, "description", "") or ""
        print(f"→ {state.__class__.__name__}: {desc}".strip())

    controller.register_connection_status_subscriber(on_status)

    print("Connecting to fastest server...")
    connect_future = controller.connect_to_fastest_server()
    try:
        await run_blocking_future(connect_future)
        print("Connected to Proton VPN!")
    except Exception as e:
        print("Connection failed:", e)
        return

    print("\nConnected! Press Ctrl+C to disconnect.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        await run_blocking_future(controller.disconnect())
        print("Disconnected. Bye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted.")
