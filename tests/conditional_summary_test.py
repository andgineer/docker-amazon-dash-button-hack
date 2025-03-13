from datetime import datetime
from unittest.mock import Mock, patch

import models


def button_actions():
    return [
        models.ActionItemLoad(
            {
                "summary": [
                    {"summary": "summary1", "before": "10:00:00", "image": "morning.png"},
                    {"summary": "summary2", "before": "19:00:00", "image": "evening.png"},
                ],
                "type": "openhab",
                "path": "path",
                "item": "item",
                "command": "command",
            }
        )
    ]


@patch("action.datetime")
def test_first_interval(fake_datetime, action):
    fake_datetime.now = Mock(return_value=datetime.strptime("00:00:00", "%H:%M:%S"))
    assert action.set_summary_by_time(button_actions()) == [
        models.OpenhabAction(
            summary="summary1", type="openhab", path="path", item="item", command="command"
        )
    ]


@patch("action.datetime")
def test_interval(fake_datetime, action):
    fake_datetime.now = Mock(return_value=datetime.strptime("19:00:00", "%H:%M:%S"))
    assert action.set_summary_by_time(button_actions()) == [
        models.OpenhabAction(
            summary="summary2", type="openhab", path="path", item="item", command="command"
        )
    ]
