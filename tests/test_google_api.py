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
    # Temporarily mock the `get_credentials_http` and `get_service` for instantiation
    with patch.object(GoogleApi, 'get_credentials_http', return_value=Mock()), patch.object(GoogleApi, 'get_service', return_value=Mock()):
        instance = GoogleApi(google_api_settings, Mock(), Mock())

    # Once the instance is created, the original methods are restored
    return instance


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


def test_get_credentials_http_failure(google_api_instance):
    with pytest.raises(ValueError) as e:
        google_api_instance.get_credentials_http()
    assert "Cannot get authorization from google API." in str(e)


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


def test_service_undefined(google_api_instance, capsys):
    google_api_instance._service = None
    with pytest.raises(ValueError) as e:
        service = google_api_instance.service()
        assert "Google API service undefined." in str(e)

