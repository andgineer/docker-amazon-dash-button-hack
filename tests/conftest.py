from unittest.mock import Mock
import sys
import pytest

# Scapy needs root privileges and we do not use it in tests so we better not import it at all

sys.modules["scapy.all"] = Mock()
sys.modules["scapy"] = Mock()
sys.modules["scapy.layers.dhcp"] = Mock()
sys.modules["scapy.layers.l2"] = Mock()

# We need to import amazon_dash after mocking scapy
from amazon_dash import AmazonDash


@pytest.fixture(scope="function")
def dash():
    return AmazonDash()