# test_google_api.py
import pytest
from google_api import GoogleApi
from unittest.mock import Mock, patch


@pytest.fixture
def google_api_settings():
    return {
        'credentials_file_name': 'path_to_credentials.json'
    }


@pytest.fixture
def google_api_instance(google_api_settings):
    return GoogleApi(google_api_settings)


def test_get_credentials_http_success(google_api_instance):
    # Mocking the ServiceAccountCredentials
    with patch('google_api.ServiceAccountCredentials.from_json_keyfile_name') as mock_method:
        mock_credentials = Mock()
        mock_method.return_value = mock_credentials

        http_instance = google_api_instance.get_credentials_http()

        # Ensure the mock credentials' authorize method was called once
        mock_credentials.authorize.assert_called_once()
        # Ensure the returned http_instance is not None (since we mocked it)
        assert http_instance is not None


def test_get_credentials_http_failure(google_api_instance, capsys):
    # Mocking the ServiceAccountCredentials to raise an exception
    with patch('google_api.ServiceAccountCredentials.from_json_keyfile_name', side_effect=Exception("Test Exception")):
        http_instance = google_api_instance.get_credentials_http()

        captured = capsys.readouterr()
        assert "Cannot get authorization from google API." in captured.out
        assert http_instance is None


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
    service = google_api_instance.get_service('calendar', 'v3')
    assert service is None


def test_service_undefined(google_api_instance, capsys):
    google_api_instance._service = None
    service = google_api_instance.service()

    captured = capsys.readouterr()
    assert "Google API service undefined." in captured.out
    assert service is None
