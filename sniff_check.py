import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from amazon_dash import sniff_arp


sniff_arp()
