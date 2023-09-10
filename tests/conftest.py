from unittest.mock import Mock
import sys

# Scapy needs root privileges and we do not use it in tests so we better not import it at all

sys.modules["scapy.all"] = Mock()
sys.modules["scapy"] = Mock()
sys.modules["scapy.layers.dhcp"] = Mock()
sys.modules["scapy.layers.l2"] = Mock()
