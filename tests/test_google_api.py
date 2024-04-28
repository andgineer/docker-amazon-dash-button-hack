import pytest
from google_api import GoogleApi
from googleapiclient.errors import UnknownApiNameOrVersion
from unittest.mock import Mock, patch


@pytest.fixture
def google_api_instance(settings, google_credentials):
    yield GoogleApi(settings, Mock(), Mock())


def test_get_credentials_http_success(google_api_instance, google_credentials):
    # Assert that from_json_keyfile_name is called in __init__
    google_credentials.assert_called_once_with(
        "../amazon-dash-private/amazon-dash-hack.json",
        [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ]
    )
    google_credentials.return_value.authorize.assert_called_once()
    assert google_api_instance.http is not None

    # Assert that from_json_keyfile_name is called with given file name
    google_api_instance.settings.credentials_file_name = "given_file_name"
    google_api_instance.get_credentials_http()
    google_credentials.assert_called_with(
        "given_file_name",
        [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ]
    )


@patch('google_api.discovery.build')
def test_get_service_with_http(mock_build, google_api_instance):
    mock_service = Mock()
    mock_build.return_value = mock_service

    # Mocking the http attribute of google_api_instance
    google_api_instance.http = Mock()

    service = google_api_instance.get_service('calendar', 'v3')

    mock_build.assert_called_once_with('calendar', 'v3', http=google_api_instance.http)
    assert service == mock_service


def test_get_service_without_http(google_api_instance):
    google_api_instance.http = None
    with pytest.raises(ValueError) as e:
        google_api_instance.get_service('calendar', 'v3')
    assert "Google API is not authorized" in str(e)


def test_service_undefined(google_api_instance, capsys, monkeypatch):
    with pytest.raises(UnknownApiNameOrVersion) as e:
        google_api_instance.service


