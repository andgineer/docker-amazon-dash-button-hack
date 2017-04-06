"""
Amazon Button (dash) press handler

Sniff for ARP traffic
"""

from scapy.all import *

def arp_handler(pkt):
    """
    Handles sniffed ARP requests
    """
    BUTTONS = {
        '34:d2:70:a4:e0:50': 'poof'
    }
    if pkt.haslayer(ARP):
        if pkt[ARP].op == 1: #who-has request
            if pkt[ARP].hwsrc in BUTTONS:
                trigger(BUTTONS[pkt[ARP].hwsrc])
            else:
                print('ARP request from unknown MAC:{}'.format(pkt[ARP].hwsrc))

def trigger(button):
    """
    Button press action
    """
    print('Button {} pressed'.format(button))


def main():
    logging.getLogger('amazon_dash').setLevel(logging.ERROR)
    sniff(prn=arp_handler, filter="arp", store=0)

main()