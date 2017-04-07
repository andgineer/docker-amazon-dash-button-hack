"""
Amazon Button (dash) press handler

Sniff for ARP traffic
"""

from scapy.all import *
from google_sheet import Sheet
import json


BUTTONS_FILE_NAME = 'amazone-dash-private/buttons.json'

buttons = {}
seen_macs = set()


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
    sheet = Sheet()
    sheet.press(button)
    sheet.event(button)


def main():
    global buttons
    buttons = load_buttons()
    print('amazon_dash started, loaded {} buttons'.format(len(buttons)))
    sniff(prn=arp_handler, filter="arp", store=0)

main()
