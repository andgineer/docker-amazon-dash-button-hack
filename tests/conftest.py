import json
from unittest.mock import Mock, patch
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
from models import Settings, EventActions
from action import Action


@pytest.fixture(scope="function")
def dash() -> AmazonDash:
    return AmazonDash()


@pytest.fixture
def settings() -> Settings:
    print("*" * 10, "load_settings")
    with open("tests/resources/settings.json", "r", encoding="utf-8") as settings_file:
        settings = Settings(**json.loads(settings_file.read()))
    return settings


@pytest.fixture
def action(settings):
    return Action(settings)


@pytest.fixture
def google_credentials():
    with patch('google_api.ServiceAccountCredentials.from_json_keyfile_name') as mock_from_json:
        mock_from_json.return_value = Mock()
        yield mock_from_json
