import json

import pytest
from ifttt import Ifttt
from requests.exceptions import RequestException


def test_load_key(mocker, settings):
    mocker.patch("builtins.open", mocker.mock_open(read_data='{"key": "sample_key"}'))

    ifttt = Ifttt(settings)

    assert ifttt.key == "sample_key"


def test_press_success(mocker, requests_mock, capsys):
    mocker.patch.object(Ifttt, 'load_key', return_value={"key": "sample_key"})

    settings = {"ifttt_key_file_name": "sample_key_file_name"}
    ifttt = Ifttt(settings)

    url = "https://maker.ifttt.com/trigger/summary/with/key/sample_key"
    mock_request = requests_mock.post(url, text='OK', status_code=200)

    ifttt.press("summary", "value1", "value2", "value3")

    # Assertions
    assert mock_request.called
    assert mock_request.call_count == 1

    request_payload = json.loads(mock_request.last_request.text)
    assert request_payload["value1"] == "value1"
    assert request_payload["value2"] == "value2"
    assert request_payload["value3"] == "value3"

    captured = capsys.readouterr()
    assert "error" not in captured.out.lower()  # Assuming all error messages contain the word "error"
    assert "fail" not in captured.out.lower()  # Assuming failure messages contain the word "fail"


def test_press_failure_status_code(mocker, requests_mock, capsys):
    mocker.patch.object(Ifttt, 'load_key', return_value={"key": "sample_key"})

    settings = {"ifttt_key_file_name": "sample_key_file_name"}
    ifttt = Ifttt(settings)

    url = "https://maker.ifttt.com/trigger/summary/with/key/sample_key"
    requests_mock.post(url, text='Bad Request', status_code=400)

    ifttt.press("summary", "value1", "value2", "value3")
    captured = capsys.readouterr()

    assert "*" * 10 + " IFTTT error:\n" in captured.out


def test_press_request_exception(mocker, requests_mock, capsys):
    mocker.patch.object(Ifttt, 'load_key', return_value={"key": "sample_key"})

    settings = {"ifttt_key_file_name": "sample_key_file_name"}
    ifttt = Ifttt(settings)

    url = "https://maker.ifttt.com/trigger/summary/with/key/sample_key"
    requests_mock.post(url, exc=RequestException)

    ifttt.press("summary", "value1", "value2", "value3")
    captured = capsys.readouterr()

    assert "*" * 10 + " IFTTT request fail:\n" in captured.out
