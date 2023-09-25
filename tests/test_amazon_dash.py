import pytest
import json
import os
from datetime import datetime
from amazon_dash import BOUNCE_DELAY


def test_button_file_name(dash):
    result = dash.button_file_name(os.path.join("", "test"))
    expected = os.path.join("", "test", "amazon-dash-private", "buttons.json")
    assert result == expected


def test_setting_file_name(dash):
    result = dash.setting_file_name(os.path.join("", "test"))
    expected = os.path.join("", "test", "amazon-dash-private", "settings.json")
    assert result == expected


def test_json_safe_loads_valid(dash):
    data = '{"key": "value"}'
    result = dash.json_safe_loads(data)
    assert result == {"key": "value"}


def test_json_safe_loads_invalid(dash):
    data = '{"key": "value"'
    with pytest.raises(json.decoder.JSONDecodeError):
        dash.json_safe_loads(data)


def test_load_settings_valid(mocker, dash):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps({"key": "value"})))
    result = dash.load_settings()
    assert result == {"key": "value"}


def test_load_settings_no_file(mocker, dash):
    mocker.patch('os.path.isfile', return_value=False)
    with pytest.raises(SystemExit):
        dash.load_settings()


def test_load_buttons_valid(mocker, dash):
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps({"MAC1": "Button1"})))
    result = dash.load_buttons()
    assert result == {"MAC1": "Button1"}


def test_load_buttons_no_file(mocker, dash):
    mocker.patch('os.path.isfile', return_value=False)
    with pytest.raises(SystemExit):
        dash.load_buttons()


@pytest.mark.parametrize(
    "current_time, chatter_time, expected",
    [
        (datetime(2023, 9, 13, 12, 0, BOUNCE_DELAY - 1), datetime(2023, 9, 13, 12, 0, 0), False),
        (datetime(2023, 9, 13, 12, 0, 0), datetime(2023, 9, 13, 11, 54, 0), True),
    ],
)
def test_trigger_debouncing(mocker, dash, current_time, chatter_time, expected):
    dash.debounce = {"button1": {"time": chatter_time}}
    mock_action = mocker.patch('amazon_dash.Action')

    call_action = mock_action.return_value.action
    dash.trigger("button1", current_time)

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


def test_arp_handler_known_mac(mocker, dash):
    # Create a fake packet instance
    pkt = mocker.MagicMock()
    known_mac = "00:11:22:33:44:55"
    pkt.src = known_mac
    pkt.haslayer.return_value = True
    pkt.time = 1234567890
    pkt["ARP"].op = 1  # Mocking the who_has_request as True

    # Set up your test scenario
    dash.buttons = {known_mac: "TestButton"}
    mock_trigger = mocker.patch('amazon_dash.AmazonDash.trigger')

    dash.arp_handler(pkt)
    mock_trigger.assert_called_once_with("TestButton", datetime.fromtimestamp(pkt.time))


def test_run(mocker, dash):
    # Mock necessary functions
    mocker.patch.object(dash, 'load_buttons', return_value={})
    mocker.patch.object(dash, 'load_settings', return_value={})
    mock_sniff = mocker.patch('amazon_dash.sniff')

    dash.run()
    mock_sniff.assert_called_once()
