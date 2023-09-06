from datetime import datetime
from unittest.mock import Mock, patch

from action import Action
from amazon_dash import load_settings


@patch("action.datetime")
def test_action(fake_datetime):
    fake_datetime.now = Mock(return_value=datetime.strptime("19:00:00", "%H:%M:%S"))
    settings = load_settings(
        "."
    )  # we run tests from outside src folder so we have to change path to settings file
    act = Action(settings)
    act.ifttt_action = Mock()
    act.calendar_action = Mock()
    act.sheet_action = Mock()
    act.action("white")
    act.ifttt_action.assert_called_with(
        "white",
        {
            "type": "ifttt",
            "summary": "white_amazon_dash",
            "value1": "",
            "value2": "",
            "value3": "",
        },
    )
    act.calendar_action.assert_called_with(
        "white",
        {
            "type": "calendar",
            "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
            "dashboard": "anna_work_out",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
            "summary": "Physiotherapy",
        },
    )
    act.sheet_action.assert_called_with(
        "white",
        {
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
            "summary": "Physiotherapy",
        },
    )
