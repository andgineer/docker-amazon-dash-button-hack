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


def button_file_name(root):
    return os.path.join(root, 'amazon-dash-private', 'buttons.json')


def setting_file_name(root):
    return os.path.join(root, 'amazon-dash-private', 'settings.json')

buttons = {}
settings = {}
seen_macs = set()
seen_dhcp = set()
de_chatter = {}  # chatter protection (multiple packets less that chatter_delay)


NO_SETTINGS_FILE = '''\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro'''

def json_safe_loads(str):
    try:
        return json.loads(str)
    except:
        print('\n', '!'*5, 'Wrong json:\n', str)
        raise

def load_settings(settings_folder='..'):
    """ Load settings """
    if not os.path.isfile(setting_file_name(settings_folder)):
        print(NO_SETTINGS_FILE.format(setting_file_name(settings_folder)))
        exit(1)
    with open(setting_file_name(settings_folder), 'r', encoding='utf-8-sig') as settings_file:
        return json_safe_loads(settings_file.read())


def load_buttons(settings_folder='..'):
    """ Load known buttons """
    if not os.path.isfile(button_file_name(settings_folder)):
        print(NO_SETTINGS_FILE.format(button_file_name(settings_folder)))
        exit(1)
    with open(button_file_name(settings_folder), 'r', encoding='utf-8-sig') as buttons_file:
        buttons = json_safe_loads(buttons_file.read())
    return buttons


def arp_handler(pkt):
    """ Handles sniffed ARP and DHCP requests """
    who_has_request = 1
    if pkt.haslayer(ARP) and pkt[ARP].op == who_has_request \
        or pkt.haslayer(DHCP):
            mac = pkt.src  # pkt[layer].hwsrc
            if mac in buttons:
                trigger(buttons[mac])
            else:
                if pkt.haslayer(DHCP) and mac not in seen_dhcp:
                    print('DHCP request from unknown MAC {}:\n{}'.format(mac, pkt[DHCP].options))
                    seen_dhcp.add(mac)
                if mac not in seen_macs and mac not in seen_dhcp:
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


def sniff_arp():
    sniff(prn=arp_handler, store=0, filter='arp or (udp and port 67)')


def main():
    global buttons, settings, chatter_delay

    buttons = load_buttons()
    settings = load_settings()
    chatter_delay = int(settings.get('chatter_delay', 5))
    print('amazon_dash started, loaded {} buttons'.format(len(buttons)))
    sniff_arp()


if __name__ == '__main__':
    main()
