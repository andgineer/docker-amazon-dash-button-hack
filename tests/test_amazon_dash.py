# test_amazon_dash.py

import pytest

import amazon_dash
import json
from datetime import datetime
import os


def test_button_file_name():
    result = amazon_dash.button_file_name("/test/")
    expected = os.path.join("/test", "amazon-dash-private", "buttons.json")
    assert result == expected

def test_setting_file_name():
    result = amazon_dash.setting_file_name("/test/")
    expected = os.path.join("/test", "amazon-dash-private", "settings.json")
    assert result == expected



def test_json_safe_loads_valid():
    data = '{"key": "value"}'
    result = amazon_dash.json_safe_loads(data)
    assert result == {"key": "value"}


def test_json_safe_loads_invalid():
    data = '{"key": "value"'
    with pytest.raises(Exception):
        amazon_dash.json_safe_loads(data)


def test_load_settings_valid(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps({"key": "value"})))
    result = amazon_dash.load_settings()
    assert result == {"key": "value"}


def test_load_settings_no_file(mocker):
    mocker.patch('os.path.isfile', return_value=False)
    with pytest.raises(SystemExit):
        amazon_dash.load_settings()


def test_load_buttons_valid(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps({"MAC1": "Button1"})))
    result = amazon_dash.load_buttons()
    assert result == {"MAC1": "Button1"}


def test_load_buttons_no_file(mocker):
    mocker.patch('os.path.isfile', return_value=False)
    with pytest.raises(SystemExit):
        amazon_dash.load_buttons()


@pytest.mark.parametrize(
    "current_time, chatter_time, expected",
    [
        (datetime(2023, 9, 13, 12, 0, amazon_dash.chatter_delay - 1), datetime(2023, 9, 13, 12, 0, 0), False),
        (datetime(2023, 9, 13, 12, 0, 0), datetime(2023, 9, 13, 11, 54, 0), True),
    ],
)
def test_trigger_chatter_protection(mocker, current_time, chatter_time, expected):
    amazon_dash.de_chatter = {"button1": {"time": chatter_time}}
    mocker.patch('amazon_dash.datetime', MockDateTime(current_time))

    mock_action = mocker.patch('amazon_dash.Action')

    call_action = mock_action.return_value.action
    amazon_dash.trigger("button1")

    if expected:
        call_action.assert_called_once()
    else:
        call_action.assert_not_called()


class MockDateTime:
    @classmethod
    def now(cls):
        return cls.current_time

    def __init__(self, current_time):
        MockDateTime.current_time = current_time


def test_arp_handler_known_mac(mocker):
    known_mac = "00:11:22:33:44:55"
    amazon_dash.buttons = {known_mac: "TestButton"}
    mock_trigger = mocker.patch('amazon_dash.trigger')

    pkt = Packet()
    pkt.src = known_mac
    pkt[ARP].op = 1  # who_has_request

    amazon_dash.arp_handler(pkt)
    mock_trigger.assert_called_once_with("TestButton")


def test_arp_handler_known_mac(mocker):
    # Create a fake packet instance
    pkt = mocker.MagicMock()
    known_mac = "00:11:22:33:44:55"
    pkt.src = known_mac
    pkt.haslayer.return_value = True
    pkt["ARP"].op = 1  # Mocking the who_has_request as True

    # Set up your test scenario
    amazon_dash.buttons = {known_mac: "TestButton"}
    mock_trigger = mocker.patch('amazon_dash.trigger')

    amazon_dash.arp_handler(pkt)
    mock_trigger.assert_called_once_with("TestButton")


def test_run(mocker):
    # Mock necessary functions
    mocker.patch('amazon_dash.load_buttons', return_value={})
    mocker.patch('amazon_dash.load_settings', return_value={})
    mock_sniff = mocker.patch('amazon_dash.sniff')

    amazon_dash.run()
    mock_sniff.assert_called_once()


