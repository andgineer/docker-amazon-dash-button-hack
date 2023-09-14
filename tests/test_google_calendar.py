# tests/test_google_calendar.py
import time

import pytest
from unittest.mock import patch, Mock, MagicMock
import datetime
from google_calendar import Calendar
from freezegun import freeze_time

# Mock GoogleApi.get_credentials_http
@pytest.fixture
def mock_get_credentials_http():
    with patch("google_calendar.GoogleApi.get_credentials_http") as mock_method:
        mock_http = Mock()
        mock_method.return_value = mock_http
        yield mock_method


@pytest.fixture
def mock_discovery_build():
    with patch('googleapiclient.discovery.build') as mock_build:
        yield mock_build


@pytest.fixture
def mock_calendar(mock_get_credentials_http, mock_discovery_build):
    settings = {"test": "setting", "credentials_file_name": "test_credentials.json"}
    calendar_id = "test_calendar_id"
    with patch('google_calendar.GoogleApi', return_value=Mock()):
        calendar = Calendar(settings, calendar_id)
    return calendar


@freeze_time("2023-09-14T10:42:01")
def test_start_event(mock_calendar):
    mock_calendar.start_event("Test Event")
    tz = int(-time.timezone / 60 / 60 * 100)
    event_body = {
        'summary': 'Test Event',
        'description': 'Event created by amazon dash (button) click.',
        'start': {'dateTime': f'2023-09-14T10:42:01+{tz // 100:02d}:{abs(tz % 100):02d}'},
        'end': {'dateTime': f'2023-09-14T10:42:01+{tz // 100:02d}:{abs(tz % 100):02d}'}
    }
    mock_calendar.service().events().insert.assert_called_with(calendarId=mock_calendar.calendarId, body=event_body)
    mock_calendar.service().events().insert().execute.assert_called_once()


def test_get_last_event(mock_calendar):
    mock_calendar.service().events().list.return_value.execute.return_value = {
        'items': [{
            'start': {'dateTime': '2023-01-01T00:00:00Z'},
            'end': {'dateTime': '2023-01-01T01:00:00Z'},
            'summary': 'Test Event',
            'id': '123'
        }]
    }
    event_id, event = mock_calendar.get_last_event("Test Event")
    assert event_id == '123'
    assert event[0] == 'Test Event'
    assert isinstance(event[1], datetime.datetime)

def test_delete_event(mock_calendar):
    mock_calendar.delete_event("123")
    assert mock_calendar.service().events().delete.call_count == 1

def test_close_event(mock_calendar):
    mock_calendar.close_event("123", datetime.datetime.now())
    assert mock_calendar.service().events().update.call_count == 1

def test_google_api_get_credentials_http(mock_get_credentials_http):
    # This test checks if the get_credentials_http method was mocked correctly
    settings = {"test": "setting", "credentials_file_name": "test_credentials.json"}
    calendar_id = "test_calendar_id"
    calendar = Calendar(settings, calendar_id)
    assert calendar.http is not None
    mock_get_credentials_http.assert_called_once()

