"""
Amazon Dash Button server

Sniff for ARP traffic and detects amazon dash (button) press.
Register events in class Action
"""

from scapy.all import *
from action import Action
import json
import os.path
from datetime import datetime, timedelta


BUTTONS_FILE_NAME = '../amazon-dash-private/buttons.json'
SETTINGS_FILE_NAME = '../amazon-dash-private/settings.json'

buttons = {}
settings = {}
seen_macs = set()
de_chatter = {}  # chatter protection (multiple packets less that chatter_delay)


NO_SETTINGS_FILE = '''\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro'''

def load_settings():
    """ Load settings """
    if not os.path.isfile(SETTINGS_FILE_NAME):
        print(NO_SETTINGS_FILE.format(SETTINGS_FILE_NAME))
        exit(1)
    with open(SETTINGS_FILE_NAME, 'r', encoding='utf-8-sig') as settings_file:
        return json.loads(settings_file.read())


def load_buttons():
    """ Load known buttons """
    if not os.path.isfile(BUTTONS_FILE_NAME):
        print(NO_SETTINGS_FILE.format(BUTTONS_FILE_NAME))
        exit(1)
    with open(BUTTONS_FILE_NAME, 'r', encoding='utf-8-sig') as buttons_file:
        buttons = json.loads(buttons_file.read())
    return buttons


def arp_handler(pkt):
    """ Handles sniffed ARP and DHCP requests """
    who_has_request = 1
    if pkt.haslayer(ARP) and pkt[ARP].op == who_has_request \
        or pkt.haslayer(DHCP):
            mac = pkt.src  # pkt[layer].hwsrc
            if pkt.haslayer(DHCP):
                print('DHCP request from MAC {}:\n{}'.format(mac, pkt[DHCP].options))
            if mac in buttons:
                trigger(buttons[mac])
            else:
                if mac not in seen_macs:
                    print('Network request from unknown MAC {}'.format(mac))
                    seen_macs.add(mac)


def trigger(button):
    """ Button press action """
    if button in de_chatter:
        if de_chatter[button]['time'] + timedelta(seconds=chatter_delay) > datetime.now():
            print('Chatter protection. Skip this network request from "{}" as duplicate (see "chatter_delay" in settings).'.format(button))
            return
    de_chatter[button] = {'time': datetime.now()}
    print('button "{}" pressed'.format(button))
    Action(settings).action(button)


def main():
    global buttons, settings, chatter_delay

    buttons = load_buttons()
    settings = load_settings()
    chatter_delay = int(settings.get('chatter_delay', 5))
    print('amazon_dash started, loaded {} buttons'.format(len(buttons)))
    sniff(prn=arp_handler, store=0, filter='arp or (udp and port 67)')


if __name__ == '__main__':
    main()
