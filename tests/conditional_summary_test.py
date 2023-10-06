from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

import models
from action import Action


def button_actions():
    return [
        models.ActionItemLoad({
            "summary": [
                {"summary": "summary1", "before": "10:00:00", "image": "morning.png"},
                {"summary": "summary2", "before": "19:00:00", "image": "evening.png"},
            ],
            "type": "openhab",
            "path": "path",
            "item": "item",
            "command": "command",
        })
    ]


class ConditionalSummary(TestCase):
    def setUp(self):
        self.action = Action({"events": []})

    @patch("action.datetime")
    def test_first_interval(self, fake_datetime):
        fake_datetime.now = Mock(return_value=datetime.strptime("00:00:00", "%H:%M:%S"))
        assert self.action.set_summary_by_time(button_actions()) == [
            models.OpenhabAction(summary="summary1", type="openhab", path="path", item="item", command="command")
        ]

    @patch("action.datetime")
    def test_interval(self, fake_datetime):
        fake_datetime.now = Mock(return_value=datetime.strptime("19:00:00", "%H:%M:%S"))
        assert self.action.set_summary_by_time(button_actions()) == [
            models.OpenhabAction(summary="summary2", type="openhab", path="path", item="item", command="command")
        ]
