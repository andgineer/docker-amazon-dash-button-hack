from amazon_dash import load_settings
import action
from unittest.mock import patch, Mock
from datetime import datetime
from copy import deepcopy


def test_action():
    settings = load_settings()
    act = action.Action(settings)
    act.ifttt_action = Mock()
    act.calendar_action = Mock()
    act.sheet_action = Mock()
    act.action('white')
    act.ifttt_action.assert_called_with('white', {'type': 'ifttt', 'summary': 'white_amazon_dash', 'value1': '', 'value2': '', 'value3': ''})
    act.calendar_action.assert_called_with('white', {'type': 'calendar', 'calendar_id': 'eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com', 'dashboard': 'anna_work_out', 'restart': 15, 'autoclose': 10800, 'default': 900, 'summary': 'Physiotherapy'})
    act.sheet_action.assert_called_with('white', {'type': 'sheet', 'name': 'amazon_dash', 'press_sheet': 'press', 'event_sheet': 'event', 'restart': 15, 'autoclose': 10800, 'default': 900, 'summary': 'Physiotherapy'})


def test_preprocess():
    preprocessed = action.Action({'actions': []}).preprocess_actions('white', {
      "summary": [
        {"summary": "Morning work-out", "before": "12:00:00", "image": "morning.png"},
        {"summary": "Physiotherapy", "image": "evening2.png"}
      ],
      "actions": [
        {
          "type": "sheet",
          "name": "amazon_dash",
          "press_sheet": "press",
          "event_sheet": "event",
          "restart": 15,
          "autoclose": 10800,
          "default": 900
        },
        {
          "type": "calendar",
          "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
          "dashboard": "anna_work_out",
          "restart": 15,
          "autoclose": 10800,
          "default": 900
        },
        {
          "type": "ifttt",
          "summary": "{button}_amazon_dash",
          "value1": "",
          "value2": "",
          "value3": ""
        }
      ]
    })
    assert preprocessed == [
        {'type': 'sheet', 'name': 'amazon_dash', 'press_sheet': 'press', 'event_sheet': 'event', 'restart': 15,
         'autoclose': 10800, 'default': 900, 'summary': [
            {'summary': 'Morning work-out', 'before': '12:00:00', 'image': 'morning.png'},
            {'summary': 'Physiotherapy', 'image': 'evening2.png'}
        ]},
        {'type': 'calendar', 'calendar_id': 'eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com',
         'dashboard': 'anna_work_out', 'restart': 15, 'autoclose': 10800, 'default': 900, 'summary': [
            {'summary': 'Morning work-out', 'before': '12:00:00', 'image': 'morning.png'},
            {'summary': 'Physiotherapy', 'image': 'evening2.png'}]},
        {'type': 'ifttt', 'summary': 'white_amazon_dash', 'value1': '', 'value2': '', 'value3': ''}
    ]


button_actions = [
    {"summary": [
            {"summary": "summary1", "before": "10:00:00"},
            {"summary": "summary2", "before": "19:00:00"}
        ]
        }
    ]


@patch('action.datetime')
def test_action_conditional_summary_first_interval(fake_datetime):
    fake_datetime.now = Mock(return_value=datetime.strptime('00:00:00', '%H:%M:%S'))
    assert action.Action({'actions': []}).set_summary_by_time(deepcopy(button_actions)) == [{'summary': 'summary1'}]


@patch('action.datetime')
def test_action_conditional_summary_second_interval(fake_datetime):
    fake_datetime.now = Mock(return_value=datetime.strptime('19:00:00', '%H:%M:%S'))
    assert action.Action({'actions': []}).set_summary_by_time(deepcopy(button_actions)) == [{'summary': 'summary2'}]



