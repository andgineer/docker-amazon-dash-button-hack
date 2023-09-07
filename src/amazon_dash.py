"""Amazon Dash Button server.

Sniff for ARP traffic and detects amazon dash (button) press.
Register events in class Action
"""

import json
import os.path
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Set

from scapy.all import Packet, sniff
from scapy.layers.dhcp import DHCP
from scapy.layers.l2 import ARP

from action import Action


def button_file_name(root: str) -> str:
    """Return button file name."""
    return os.path.join(root, "amazon-dash-private", "buttons.json")


def setting_file_name(root: str) -> str:
    """Return settings file name."""
    return os.path.join(root, "amazon-dash-private", "settings.json")


buttons: Dict[str, Any] = {}
settings: Dict[str, Any] = {}
seen_macs: Set[str] = set()
seen_dhcp: Set[str] = set()
de_chatter: Dict[
    str, Dict[str, Any]
] = {}  # chatter protection (multiple packets less that chatter_delay)
chatter_delay: int = 5


NO_SETTINGS_FILE = """\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro"""


def json_safe_loads(text: str) -> Dict[str, Any]:
    """Load json from string."""
    try:
        return json.loads(text)  # type: ignore
    except:
        print("\n", "!" * 5, "Wrong json:\n", text)
        raise


def load_settings(settings_folder: str = "..") -> Dict[str, Any]:
    """Load settings."""
    if not os.path.isfile(setting_file_name(settings_folder)):
        print(NO_SETTINGS_FILE.format(setting_file_name(settings_folder)))
        sys.exit(1)
    with open(setting_file_name(settings_folder), "r", encoding="utf-8-sig") as settings_file:
        return json_safe_loads(settings_file.read())


def load_buttons(settings_folder: str = "..") -> Dict[str, Any]:
    """Load known buttons."""
    if not os.path.isfile(button_file_name(settings_folder)):
        print(NO_SETTINGS_FILE.format(button_file_name(settings_folder)))
        sys.exit(1)
    with open(button_file_name(settings_folder), "r", encoding="utf-8-sig") as buttons_file:
        buttons = json_safe_loads(buttons_file.read())
    return buttons


def arp_handler(pkt: Packet) -> None:
    """Handle sniffed ARP and DHCP requests."""
    who_has_request = 1
    if pkt.haslayer(ARP) and pkt[ARP].op == who_has_request or pkt.haslayer(DHCP):
        mac = pkt.src  # pkt[layer].hwsrc
        if mac in buttons:
            trigger(buttons[mac])
        else:
            if pkt.haslayer(DHCP) and mac not in seen_dhcp:
                print(f"DHCP request from unknown MAC {mac}:\n{pkt[DHCP].options}")
                seen_dhcp.add(mac)
            if mac not in seen_macs and mac not in seen_dhcp:
                print(f"Network request from unknown MAC {mac}")
                seen_macs.add(mac)


def trigger(button: str) -> None:
    """Button press action."""
    if (
        button in de_chatter
        and de_chatter[button]["time"] + timedelta(seconds=chatter_delay) > datetime.now()
    ):
        print(
            f'Chatter protection. Skip this network request from "{button}" as duplicate (see "chatter_delay" in settings).'
        )
        return
    de_chatter[button] = {"time": datetime.now()}
    print(f'button "{button}" pressed')
    Action(settings).action(button)


def sniff_arp() -> None:
    """Sniff for ARP and DHCP requests."""
    sniff(prn=arp_handler, store=0, filter="arp or (udp and port 67)")


def run() -> None:
    """Run server."""
    global buttons, settings, chatter_delay

    buttons = load_buttons()
    settings = load_settings()
    chatter_delay = int(settings.get("chatter_delay", chatter_delay))
    print(f"amazon_dash started, loaded {len(buttons)} buttons")
    sniff_arp()


if __name__ == "__main__":  # pragma: no cover
    run()
