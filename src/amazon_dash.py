"""Amazon Dash Button server.

Sniff for ARP traffic and detects amazon dash (button) press.
Register events in class Action
"""

import os.path
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

from scapy.all import Packet, sniff
from scapy.layers.dhcp import DHCP
from scapy.layers.l2 import ARP

import models
from action import Action

NO_SETTINGS_FILE = """\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro"""


class AmazonDash:
    """Amazon Dash Button server."""

    def __init__(self) -> None:
        """Init."""
        self.buttons: Dict[str, Any] = {}
        self.settings: Optional[models.Settings] = None
        self.seen_macs: Set[str] = set()
        self.seen_dhcp: Set[str] = set()
        self.debounce: Dict[  # bounce protection (repeated packets in less than bounce_delay from last event)
            str, Dict[str, Any]
        ] = {}

    @staticmethod
    def button_file_name(root: str) -> str:
        """Return button file name."""
        return os.path.join(root, "amazon-dash-private", "buttons.json")

    @staticmethod
    def setting_file_name(root: str) -> str:
        """Return settings file name."""
        return os.path.join(root, "amazon-dash-private", "settings.json")

    def load_settings(self, settings_folder: str = "..") -> models.Settings:
        """Load settings."""
        if not os.path.isfile(self.setting_file_name(settings_folder)):
            print(NO_SETTINGS_FILE.format(self.setting_file_name(settings_folder)))
            sys.exit(1)
        with open(
            self.setting_file_name(settings_folder), "r", encoding="utf-8-sig"
        ) as settings_file:
            return models.Settings.model_validate_json(settings_file.read())

    def load_buttons(self, settings_folder: str = "..") -> Dict[str, Any]:
        """Load known buttons."""
        if not os.path.isfile(self.button_file_name(settings_folder)):
            print(NO_SETTINGS_FILE.format(self.button_file_name(settings_folder)))
            sys.exit(1)
        with open(
            self.button_file_name(settings_folder), "r", encoding="utf-8-sig"
        ) as buttons_file:
            buttons = models.ButtonMacs.model_validate_json(buttons_file.read()).model_dump(
                exclude_none=True
            )
        return buttons

    def arp_handler(self, pkt: Packet) -> None:
        """Handle sniffed ARP and DHCP requests."""
        who_has_request = 1
        if pkt.haslayer(ARP) and pkt[ARP].op == who_has_request or pkt.haslayer(DHCP):
            mac = pkt.src  # pkt[layer].hwsrc
            if mac in self.buttons:
                self.trigger(self.buttons[mac], datetime.fromtimestamp(pkt.time))
            else:
                if pkt.haslayer(DHCP) and mac not in self.seen_dhcp:
                    print(f"DHCP request from unknown MAC {mac}:\n{pkt[DHCP].options}")
                    self.seen_dhcp.add(mac)
                if mac not in self.seen_macs and mac not in self.seen_dhcp:
                    print(f"Network request from unknown MAC {mac}")
                    self.seen_macs.add(mac)

    def is_bounced(self, button: str, press_time: datetime) -> bool:
        """Check if the button is pressed too recently and the press should be ignored.

        If this is not bouncing we register the press in debounce dict.
        """
        assert self.settings is not None
        if (
            button in self.debounce
            and self.debounce[button]["time"] + timedelta(seconds=self.settings.bounce_delay)
            > press_time
        ):
            return True

        self.debounce[button] = {"time": press_time}
        return False

    def trigger(self, button: str, press_time: datetime) -> None:
        """Button press action."""
        assert self.settings is not None
        if self.is_bounced(button, press_time):
            print(
                f'Bounce protection. Skip this network request from "{button}" as duplicate (see "bounce_delay" in settings).'
            )
            return
        print(f'button "{button}" pressed')
        Action(self.settings).action(button)

    def sniff_arp(self) -> None:
        """Sniff for ARP and DHCP requests."""
        sniff(prn=self.arp_handler, store=0, filter="arp or (udp and port 67)")

    def run(self) -> None:
        """Run server."""
        self.buttons = self.load_buttons()
        self.settings = self.load_settings()
        print(f"amazon_dash started, loaded {len(self.buttons)} buttons")
        self.sniff_arp()


if __name__ == "__main__":  # pragma: no cover
    amazon_dash = AmazonDash()
    amazon_dash.run()
