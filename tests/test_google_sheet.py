from datetime import datetime, timedelta

import pytest
from unittest.mock import Mock, patch, PropertyMock
from google_sheet import Sheet


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
def mock_sheet(mock_get_credentials_http, mock_discovery_build):
    settings = {"test": "setting", "credentials_file_name": "test_credentials.json"}
    sheet_name = "test_calendar_id"
    with patch('google_calendar.GoogleApi', return_value=Mock()), patch('google_sheet.Sheet.get_file_id', return_value="test_id"):
        sheet = Sheet(settings, sheet_name)
        with patch.object(sheet, 'service', new_callable=PropertyMock) as mock_service:
            mock_service.return_value = Mock()  # Mocking the actual Google Sheet service

            sheet.drive_service = Mock()  # Mocking the Drive service
            sheet.http = Mock()  # Mocking the http attribute

            # Mock get_file_id behavior
            sheet.drive_service = Mock()
            sheet.drive_service.files().list.return_value.execute.return_value = {'files': [{'id': 'test_id', 'name': 'Test Sheet Name'}]}

            return sheet


def test_get_file_id(mock_sheet):
    assert mock_sheet.get_file_id("Test Sheet Name") == "test_id"


def test_get_file_id_with_pagination(mock_sheet):
    # Given
    # Mocked responses to simulate pagination
    first_response = {
        "nextPageToken": "some_token",
        "files": [{"id": "not_the_file_we_want", "name": "Other File"}],
    }
    second_response = {
        "files": [{"id": "test_id", "name": "Test Sheet Name"}],
    }

    # Setup mock to return first_response on the first call and second_response on the second
    mock_sheet.drive_service.files().list().execute.side_effect = [first_response, second_response]

    # When
    file_id = mock_sheet.get_file_id("Test Sheet Name")

    # Then
    assert file_id == "test_id"

    # Assert that the mock was called twice (once for each page)
    assert mock_sheet.drive_service.files().list().execute.call_count == 2


def test_get_file_id_no_such_file(mock_sheet):
    # Given
    # Mocked responses to simulate pagination
    first_response = {
        "nextPageToken": "some_token",
        "files": [{"id": "not_the_file_we_want", "name": "Other File"}],
    }
    second_response = {
        "files": [{"id": "test_id", "name": "Test Sheet Name"}],
    }

    # Setup mock to return first_response on the first call and second_response on the second
    mock_sheet.drive_service.files().list().execute.side_effect = [first_response, second_response]

    # When
    file_id = mock_sheet.get_file_id("-unexisted-")

    # Then
    assert file_id is None

    # Assert that the mock was called twice (once for each page)
    assert mock_sheet.drive_service.files().list().execute.call_count == 2


def serial_to_datetime(serial: float) -> datetime:
    """Convert google 'serial number' date-time to datetime."""
    return datetime(year=1899, month=12, day=30) + timedelta(days=serial)


def test_get_last_event(mock_sheet):
    # Given
    # Mocking serial numbers for '01/01/2023 12:00:00' and '02/01/2023 12:00:00'
    mock_serial_for_start_date = (datetime(2023, 1, 1, 12, 0) - datetime(1899, 12, 30)).days
    mock_serial_for_end_date = (datetime(2023, 1, 2, 12, 0) - datetime(1899, 12, 30)).days
    mock_rows = [['summary', mock_serial_for_start_date, mock_serial_for_end_date]]
    mock_sheet.get_rows = Mock(return_value=mock_rows)

    # When
    row, event = mock_sheet.get_last_event("summary")

    # Then
    assert row == 1
    expected_event = ['summary',
                      serial_to_datetime(mock_serial_for_start_date),
                      serial_to_datetime(mock_serial_for_end_date)]
    assert event == expected_event


def test_get_last_event_not_found(mock_sheet):
    # Given
    # Mocking find_last_row method to return None for both row and event
    mock_sheet.find_last_row = Mock(return_value=(None, None))

    # When
    row, event = mock_sheet.get_last_event("summary")

    # Then
    assert row is None
    assert event is None


def test_start_event(mock_sheet):
    # Given
    current_time = datetime(2023, 1, 1, 12, 0)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = current_time
        mock_sheet.insert_row = Mock()
        mock_sheet.copy_row_formatting = Mock()
        mock_sheet.update_cells = Mock()

        # When
        mock_sheet.start_event("Test Event")

        # Then
        mock_sheet.insert_row.assert_called_once_with(sheet=mock_sheet.event_sheet)
        mock_sheet.copy_row_formatting.assert_called_once_with(sheet=mock_sheet.event_sheet)
        mock_sheet.update_cells.assert_called_once_with(
            sheet=mock_sheet.event_sheet,
            values=["Test Event", current_time.strftime("%d/%m/%Y %H:%M:%S")]
        )


def test_close_event(mock_sheet):
    # Mock the update_cells method
    mock_sheet.update_cells = Mock()

    # Given
    close_time = datetime(2023, 1, 2, 12, 0)
    event_row = 1

    # When
    mock_sheet.close_event(event_row, close_time)

    # Then
    mock_sheet.update_cells.assert_called_once_with(
        sheet=mock_sheet.event_sheet,
        row=event_row,
        col=2,
        values=[close_time.strftime("%d/%m/%Y %H:%M:%S"), "=C2-B2"]
    )


def test_press(mock_sheet):
    # Given
    current_time = datetime(2023, 1, 3, 12, 0)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = current_time
        mock_sheet.insert_row = Mock()
        mock_sheet.copy_row_formatting = Mock()
        mock_sheet.update_cells = Mock()

        # When
        mock_sheet.press("Button Pressed")

        # Then
        mock_sheet.insert_row.assert_called_once_with(sheet=mock_sheet.press_sheet)
        mock_sheet.copy_row_formatting.assert_called_once_with(sheet=mock_sheet.press_sheet)
        mock_sheet.update_cells.assert_called_once_with(
            sheet=mock_sheet.press_sheet,
            values=["Button Pressed", current_time.strftime("%d/%m/%Y %H:%M:%S")]
        )


def test_copy_row_formatting(mock_sheet):
    # Given
    mock_spreadsheets = Mock()
    mock_batch_update = Mock()

    # Mocking the sheets attribute
    mock_sheet.sheets = {"TestSheet": "mockedSheetId"}
    mock_sheet.service.spreadsheets.return_value = mock_spreadsheets
    mock_spreadsheets.batchUpdate.return_value = mock_batch_update

    # When
    mock_sheet.copy_row_formatting("TestSheet", 2, 1)

    # Then
    mock_batch_update.execute.assert_called_once()


def test_get_rows(mock_sheet):
    # Given
    mock_sheet.service.spreadsheets().values().get().execute = Mock(return_value={"values": [["A1", "B1", "C1"]]})

    # When
    rows = mock_sheet.get_rows("TestSheet", 1, 3, 3)

    # Then
    assert rows == [["A1", "B1", "C1"]]


def test_get_sheets(mock_sheet):
    mock_sheet.service.spreadsheets().get.return_value.execute.return_value = {
        "sheets": [
            {"properties": {"title": "press_sheet", "sheetId": "123"}},
            {"properties": {"title": "event_sheet", "sheetId": "456"}},
        ]
    }

    result = mock_sheet.get_sheets("press_sheet", "event_sheet")
    assert result == {"press_sheet": "123", "event_sheet": "456"}


def test_get_sheets_no_service(mock_sheet, monkeypatch):
    # Mock the entire chain of method calls
    monkeypatch.setattr(mock_sheet, "service", None)

    # When
    result = mock_sheet.get_sheets("press_sheet", "event_sheet")

    # Then
    assert result == {"press_sheet": None, "event_sheet": None}


def test_update_cells(mock_sheet):
    mock_spreadsheet_values = Mock()
    mock_sheet.service.spreadsheets().values.return_value = mock_spreadsheet_values

    mock_sheet.update_cells("TestSheet", ["value1", "value2"], 0, 0)

    mock_spreadsheet_values.update.assert_called_once()


def test_append_row(mock_sheet):
    mock_spreadsheet_values = Mock()
    mock_sheet.service.spreadsheets().values.return_value = mock_spreadsheet_values

    mock_sheet.append_row("TestSheet", ["value1", "value2"], 0)

    mock_spreadsheet_values.append.assert_called_once()


def test_insert_row(mock_sheet):
    mock_spreadsheet_values = Mock()
    mock_sheet.service.spreadsheets().values.return_value = mock_spreadsheet_values

    mock_sheet.sheets = {"TestSheet": "12345"}  # Mocking sheetId for the sheet name "TestSheet"
    mock_sheet.insert_row("TestSheet", 1)

    assert mock_sheet.service.spreadsheets().batchUpdate.called
