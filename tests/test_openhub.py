# test_openhab.py
import pytest

import models
from openhab import OpenHab
from unittest.mock import Mock, patch


@pytest.fixture
def openhab_settings():
    return {
        # sample settings for the OpenHab instance, adjust as required
        "sample_key": "sample_value"
    }


@pytest.fixture
def action_params():
    return models.OpenhabAction(
        type="openhab", path="http://demo.openhab.org:8080", item="TestItem", command="ON;OFF"
    )


@patch("openhab.requests.get")
def test_openhab_press_wrong_commands(mock_get, openhab_settings, action_params, capsys):
    openhab = OpenHab(openhab_settings)
    action_params.command = "ON"

    # Mock the requests.get response (though it won't be used in this specific test)
    mock_get.return_value = Mock(text="ON")

    openhab.press(action_params)

    captured = capsys.readouterr()
    assert 'Wrong "command" setting in openhab action' in captured.out


@patch("openhab.requests.get")
@patch("openhab.requests.post")
def test_openhab_press_switch_state(mock_post, mock_get, openhab_settings, action_params):
    openhab = OpenHab(openhab_settings)
    mock_get.return_value = Mock(text="ON")

    openhab.press(action_params)

    mock_post.assert_called_once_with(
        f"{action_params.path}/items/{action_params.item}",
        data='"OFF"',
        headers={"content-type": "application/json"},
        timeout=5,
    )


@patch("openhab.requests.get")
@patch("openhab.requests.post")
def test_openhab_press_invalid_state(mock_post, mock_get, openhab_settings, action_params, capsys):
    openhab = OpenHab(openhab_settings)
    mock_get.return_value = Mock(text="INVALID_STATE")

    openhab.press(action_params)

    captured = capsys.readouterr()
    assert f"Item {action_params.item} now in state INVALID_STATE" in captured.out
    mock_post.assert_not_called()
