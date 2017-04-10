"""
Amazon Dash Button server

Sniff for ARP traffic and detects amazon dash (button) press.
Register events in class Action
"""

from scapy.all import *
from action import Action
import json


BUTTONS_FILE_NAME = '../amazon-dash-private/buttons.json'
SETTINGS_FILE_NAME = '../amazon-dash-private/settings.json'

buttons = {}
settings = {}
seen_macs = set()


def load_settings():
    with open(SETTINGS_FILE_NAME, 'r') as settings_file:
        return json.loads(settings_file.read())


def load_buttons():
    """ Load known buttons """
    with open(BUTTONS_FILE_NAME, 'r') as buttons_file:
        buttons = json.loads(buttons_file.read())
    return buttons


def arp_handler(pkt):
    """ Handles sniffed ARP requests """
    if pkt.haslayer(ARP):
        if pkt[ARP].op == 1: #who-has request
            if pkt[ARP].hwsrc in buttons:
                trigger(buttons[pkt[ARP].hwsrc])
            else:
                if pkt[ARP].hwsrc not in seen_macs:
                    print('ARP request from unknown MAC {}'.format(pkt[ARP].hwsrc))
                    seen_macs.add(pkt[ARP].hwsrc)


def trigger(button):
    """ Button press action """
    print('button {} pressed'.format(button))
    Action(settings).action(button)


def main():
    global buttons, settings
    buttons = load_buttons()
    settings = load_settings()
    print('amazon_dash started, loaded {} buttons'.format(len(buttons)))
    sniff(prn=arp_handler, filter="arp", store=0)


if __name__ == '__main__':
    main()
