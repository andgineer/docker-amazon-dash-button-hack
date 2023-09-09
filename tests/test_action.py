from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from action import Action
from amazon_dash import load_settings
import pytest


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


@pytest.fixture
def action_instance():
    settings = {
        "actions": {
            "test_button": {
                "actions": [
                    {"type": "sheet", "name": "test", "press_sheet": "sheet1", "event_sheet": "sheet2", "summary": "test_summary"},
                ]
            }
        }
    }
    return Action(settings)


def test_set_summary_by_time(action_instance):
    button_actions = [
        {
            "summary": [
                {"summary": "morning", "before": "12:00:00"},
                {"summary": "evening"}
            ]
        }
    ]

    with patch("action.datetime") as mock_datetime:
        mock_datetime.now = Mock(return_value=datetime(2023, 9, 9, 10, 0, 0))
        result = action_instance.set_summary_by_time(button_actions)
        assert result[0]["summary"] == "morning"

        mock_datetime.now = Mock(return_value=datetime(2023, 9, 9, 13, 0, 0))
        result = action_instance.set_summary_by_time(button_actions)
        assert result[0]["summary"] == "evening"


def test_preprocess_actions(action_instance):
    result = action_instance.preprocess_actions("test_button", action_instance.actions["test_button"])
    expected_result = [
        {"type": "sheet", "name": "test", "press_sheet": "sheet1", "event_sheet": "sheet2", "summary": "test_summary"}
    ]
    assert result == expected_result


@patch.object(Action, "sheet_action")
def test_action(mock_sheet_action, action_instance):
    action_instance.action("test_button", dry_run=False)
    mock_sheet_action.assert_called()


@patch("action.Sheet")
def test_sheet_action(mock_sheet, action_instance):
    mock_sheet_instance = MagicMock()
    mock_sheet.return_value = mock_sheet_instance

    mocked_even_row = 1
    prev_event_summary = "test_summary"
    prev_event_start = datetime(2023, 9, 9, 10, 0, 0)
    mock_sheet_instance.get_last_event.return_value = (mocked_even_row, [prev_event_summary, prev_event_start])

    action_params = {
        "type": "sheet",
        "name": "test",
        "press_sheet": "sheet1",
        "event_sheet": "sheet2",
        "summary": "test_summary",
        "autoclose": 10800,
        "restart": 15,
    }

    with patch("action.datetime") as mock_datetime:
        mock_datetime.now = Mock(return_value=datetime(2023, 9, 9, 11, 0, 0))
        action_instance.sheet_action("test_button", action_params)
    mock_sheet_instance.press.assert_called_with("test_summary")


@patch("action.Calendar")
def test_calendar_action(mock_calendar, action_instance):
    mock_calendar_instance = MagicMock()
    mock_calendar.return_value = mock_calendar_instance

    prev_even_id = 1
    prev_event_summary = "test_summary"
    prev_event_start = datetime(2023, 9, 9, 10, 0, 0)
    prev_event_end = datetime(2023, 9, 9, 10, 10, 0)
    mock_calendar_instance.get_last_event.return_value = (prev_even_id, [prev_event_summary, prev_event_start, prev_event_end])

    action_params = {
        "type": "calendar",
        "calendar_id": "some_id",
        "dashboard": "some_dashboard",
        "restart": 15,
        "autoclose": 10800,
        "default": 900,
        "summary": "test_summary",
    }

    mocked_now = datetime(2023, 9, 9, 11, 0, 0)
    with patch("action.datetime") as mock_datetime:
        mock_datetime.now = Mock(return_value=mocked_now)
        action_instance.calendar_action("test_button", action_params)
    mock_calendar_instance.start_event.assert_called_with('test_summary')


@patch("action.Calendar")
def test_calendar_close_event(mock_calendar, action_instance):
    mock_calendar_instance = MagicMock()
    mock_calendar.return_value = mock_calendar_instance

    prev_even_id = 1
    prev_event_summary = "test_summary"
    prev_event_start = datetime(2023, 9, 9, 10, 0, 0)
    mock_calendar_instance.get_last_event.return_value = (prev_even_id, [prev_event_summary, prev_event_start])

    action_params = {
        "type": "calendar",
        "calendar_id": "some_id",
        "dashboard": "some_dashboard",
        "restart": 15,
        "autoclose": 10800,
        "default": 900,
        "summary": "test_summary",
    }

    mocked_now = datetime(2023, 9, 9, 11, 0, 0)
    with patch("action.datetime") as mock_datetime:
        mock_datetime.now = Mock(return_value=mocked_now)
        action_instance.calendar_action("test_button", action_params)
    mock_calendar_instance.close_event.assert_called_with(prev_even_id, mocked_now)


@patch("action.Calendar")
def test_calendar_auto_close_event(mock_calendar, action_instance):
    mock_calendar_instance = MagicMock()
    mock_calendar.return_value = mock_calendar_instance

    prev_even_id = 1
    prev_event_summary = "test_summary"
    prev_event_start = datetime(2023, 9, 9, 10, 0, 0)
    mock_calendar_instance.get_last_event.return_value = (prev_even_id, [prev_event_summary, prev_event_start])

    auto_closed_event_lenth_seconds = 900
    action_params = {
        "type": "calendar",
        "calendar_id": "some_id",
        "dashboard": "some_dashboard",
        "restart": 15,
        "autoclose": 60,
        "default": auto_closed_event_lenth_seconds,
        "summary": "test_summary",
    }

    mocked_now = datetime(2023, 9, 9, 11, 0, 0)
    with patch("action.datetime") as mock_datetime:
        mock_datetime.now = Mock(return_value=mocked_now)
        action_instance.calendar_action("test_button", action_params)
    mock_calendar_instance.close_event.assert_called_with(prev_even_id, prev_event_start + timedelta(seconds=auto_closed_event_lenth_seconds))
