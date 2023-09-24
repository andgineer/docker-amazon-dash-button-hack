from unittest.mock import Mock
import sys
import pytest

# Scapy needs root privileges and we do not use it in tests so we better not import it at all

sys.modules["scapy.all"] = Mock()
sys.modules["scapy"] = Mock()
sys.modules["scapy.layers.dhcp"] = Mock()
sys.modules["scapy.layers.l2"] = Mock()

# Point sys.path to our sources before importing anything from them
import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# We need to import amazon_dash after mocking scapy
from amazon_dash import AmazonDash


@pytest.fixture(scope="function")
def dash():
    return AmazonDash()