#!/usr/bin/env python3
import asyncio
import json
import logging
from dbus_fast.aio import MessageBus
from dbus_fast import BusType, Message, MessageType

# ── Config ─────────────────────────────────────
DEVICE_ID = "4d76022a5910415f9073cc44af2025c3"  # your phone's ID
ICON = "phone"

CONNECTED = {
    "text": ICON,
    "tooltip": "Phone connected",
    "class": "connected",
    "alt": "connected",
}
DISCONNECTED = {
    "text": ICON,
    "tooltip": "Phone disconnected",
    "class": "disconnected",
    "alt": "disconnected",
}

STATE = DISCONNECTED.copy()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("kdeconnect")


def render():
    print(json.dumps(STATE), flush=True)


async def query_device_reachability(bus: MessageBus):
    try:
        obj = bus.get_proxy_object(
            "org.kde.kdeconnect",
            f"/modules/kdeconnect/devices/{DEVICE_ID}",
        )
        dev = obj.get_interface("org.kde.kdeconnect.device")
        reachable = await dev.get_isReachable()
        new_state = CONNECTED if reachable else DISCONNECTED
    except Exception as e:
        log.debug(f"Device not available yet: {e}")
        new_state = DISCONNECTED
    global STATE
    if STATE != new_state:
        STATE = new_state
        render()


async def handle_signal(msg: Message):
    if msg.message_type != MessageType.SIGNAL:
        return
    #  and msg.member in (
    #     "deviceAdded",
    #     "deviceRemoved",
    # )
    if msg.interface == "org.kde.kdeconnect.daemon":
        path = msg.body[0] if msg.body else ""
        if DEVICE_ID in path:
            log.info(f"deviceAdded/deviceRemoved → {path}")
            await query_device_reachability(bus)
    elif (
        msg.interface == "org.kde.kdeconnect.device"
        and msg.member == "reachableChanged"
    ):
        reachable = msg.body[0] if msg.body else False
        log.info(f"reachableChanged → {'reachable' if reachable else 'not reachable'}")
        global STATE
        STATE = CONNECTED if reachable else DISCONNECTED
        render()


async def main():
    global bus
    bus = await MessageBus(bus_type=BusType.SESSION).connect()
    bus.add_message_handler(handle_signal)
    bus._add_match_rule(
        "type='signal',interface='org.kde.kdeconnect.daemon',member='deviceAdded'"
    )
    bus._add_match_rule(
        "type='signal',interface='org.kde.kdeconnect.daemon',member='deviceRemoved'"
    )
    bus._add_match_rule(
        "type='signal',interface='org.kde.kdeconnect.device',member='reachableChanged'"
    )
    bus.add_message_handler(handle_signal)
    log.info("KDE Connect Waybar module ready – monitoring your phone")
    await query_device_reachability(bus)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
