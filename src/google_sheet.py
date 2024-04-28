"""Register Amazon Dash Button events in Google Sheets using Google Sheets API."""

import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import models
from google_api import GoogleApi

GSHEET_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"


class Sheet(GoogleApi):
    """Google Sheet API wrapper."""

    def __init__(
        self,
        settings: models.Settings,
        name: str,
        press_sheet: str = "press",
        event_sheet: str = "event",
    ) -> None:
        """Init."""
        super().__init__(
            settings,
            api="sheets",
            version="v4",  # discoveryServiceUrl=('https://sheets.googleapis.com/$discovery/rest?version=v4')
        )
        self.drive_service = self.get_service(api="drive", version="v3")
        self.press_sheet = press_sheet
        self.event_sheet = event_sheet
        self.spreadSheetId = self.get_file_id(name)
        self.sheets = self.get_sheets(press_sheet, event_sheet)

    def get_last_event(self, summary: str) -> Tuple[Optional[int], Optional[List[Any]]]:
        """Get last event from Google Sheet.

        :param summary: text to search
        :return:
        <id for close event>, [summary, start, end]
        """
        row, event = self.find_last_row(sheet=self.event_sheet, search_string=summary)
        if event:
            for col in range(1, len(event)):
                event[col] = self.from_serial_time(event[col])
            return row, event
        return None, None

    def start_event(self, summary: str) -> None:
        """Start event in Google Sheet."""
        self.insert_row(sheet=self.event_sheet)
        self.copy_row_formatting(sheet=self.event_sheet)
        self.update_cells(
            sheet=self.event_sheet,
            values=[summary, datetime.datetime.now().strftime(GSHEET_TIME_FORMAT)],
        )

    def close_event(  # pylint: disable=arguments-renamed
        self,
        event_id: Union[int, str],
        close_time: datetime.datetime,
    ) -> None:
        """Close event in Google Sheet.

        row 0-based
        """
        row_num = int(event_id)
        self.update_cells(
            sheet=self.event_sheet,
            row=row_num,
            col=2,
            values=[
                close_time.strftime(GSHEET_TIME_FORMAT),
                "=C{row}-B{row}".format(row=row_num + 1),
            ],
        )

    def press(self, summary: str) -> None:
        """Register press event in Google Sheet."""
        self.insert_row(sheet=self.press_sheet)
        self.copy_row_formatting(sheet=self.press_sheet)
        self.update_cells(
            sheet=self.press_sheet,
            values=[summary, datetime.datetime.now().strftime(GSHEET_TIME_FORMAT)],
        )

    def get_file_id(self, name: str) -> Optional[str]:
        """Get file id by name.

        :param name: file name
        :return: file id
        """
        if self.drive_service:
            page_token = None
            while True:
                # Full blown page iteration from API doc
                # but in fact we will get exactly one or no one file
                response = (
                    self.drive_service.files()
                    .list(
                        q=f"name='{name}'",
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )
                for file in response.get("files", []):
                    if file.get("name") == name:
                        return file.get("id")  # type: ignore
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
        return None

    def find_last_row(
        self, sheet: str, search_string: str, search_in_col: int = 0
    ) -> Tuple[Optional[int], Optional[List[Any]]]:
        """Find last row with search_string in search_in_col column.

        Very stupid implementation, but:
        The Sheets API v4 does not currently have a direct equivalent for the Sheets API v3 structured queries.
        However, you can retrieve the relevant data and sort through it as needed in your application.
        """
        ROWS_TO_FETCH = (
            1000  # well, we have to stop somewhere and 1000 looks as good as any other limit
        )
        FIRST_ROW_TO_FETCH = 1
        rows = self.get_rows(sheet=sheet, row=FIRST_ROW_TO_FETCH, rows=ROWS_TO_FETCH, cols=3)
        row_idx = FIRST_ROW_TO_FETCH
        for row in rows:
            if len(row) >= search_in_col + 1 and row[search_in_col]:
                if row[search_in_col] == search_string:
                    return row_idx, row
                row_idx += 1
            else:
                return None, None
        return None, None

    def get_sheets(self, press_sheet: str, event_sheet: str) -> Dict[str, Any]:
        """Get sheets ids.

        Returns {sheet_name: sheet_id}
        """
        if self.service:
            request = self.service.spreadsheets().get(
                spreadsheetId=self.spreadSheetId, ranges=[], includeGridData=False
            )
            sheets = request.execute()["sheets"]
            # todo check if press_sheet and event_sheet are in the sheets
            return {
                sheet["properties"]["title"]: sheet["properties"]["sheetId"] for sheet in sheets
            }
        return {press_sheet: None, event_sheet: None}

    def update_cells(self, sheet: str, values: List[Any], row: int = 1, col: int = 0) -> None:
        """Update cells in Google Sheet.

        row and col 0-based
        """
        request = (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.spreadSheetId,
                range=f"{sheet}!{chr(ord('A') + col)}{row + 1}:{chr(ord('A') + col + len(values) - 1)}",
                valueInputOption="USER_ENTERED",
                body={
                    "majorDimension": "ROWS",
                    "values": [values],
                },
            )
        )
        request.execute()

    def append_row(self, sheet: str, values: List[Any], row: int = 1) -> None:
        """Append row to Google Sheet.

        row 0-based
        """
        _ = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadSheetId,
                range=f"{sheet}!A{row + 1}:{chr(ord('A') + len(values) - 1)}",
                valueInputOption="RAW",  # 'USER_ENTERED',
                insertDataOption="INSERT_ROWS",
                body={"majorDimension": "ROWS", "values": [values]},
            )
        )

    def insert_row(self, sheet: str, after: int = 1) -> None:
        """Insert row to Google Sheet."""
        INSERT_ROW_REQUEST = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": self.sheets[sheet],
                            "dimension": "ROWS",
                            "startIndex": after,
                            "endIndex": after + 1,
                        },
                        "inheritFromBefore": False,
                    }
                },
            ],
        }
        request = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadSheetId, body=INSERT_ROW_REQUEST
        )
        request.execute()

    def copy_row_formatting(self, sheet: str, copy_from: int = 2, copy_to: int = 1) -> None:
        """Copy row formatting from copy_from to copy_to."""
        COPY_FORMATTING_REQUEST = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": self.sheets[sheet],
                            "startRowIndex": copy_from - 1,
                            "endRowIndex": copy_from,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1000,
                        },
                        "destination": {
                            "sheetId": self.sheets[sheet],
                            "startRowIndex": copy_to - 1,
                            "endRowIndex": copy_to,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1000,
                        },
                        "pasteType": "PASTE_FORMAT",
                        "pasteOrientation": "NORMAL",
                    }
                }
            ]
        }
        request = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadSheetId, body=COPY_FORMATTING_REQUEST
        )
        request.execute()

    def get_rows(self, sheet: str, row: int = 1, rows: int = 1, cols: int = 3) -> List[List[Any]]:
        """Get rows from Google Sheet.

        row 0-based
        """
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadSheetId,
                range=f"{sheet}!A{row + 1}:{chr(ord('A') + cols - 1)}{row + rows - 1}",
                valueRenderOption="UNFORMATTED_VALUE",
            )
            .execute()
        )
        values = result.get("values", [])
        return values  # type: ignore

    def from_serial_time(self, serial: float) -> datetime.datetime:
        """Convert google 'serial number' date-time to datetime."""
        return datetime.datetime(year=1899, month=12, day=30) + datetime.timedelta(days=serial)


def check() -> None:
    """Check."""
    from amazon_dash import AmazonDash  # pylint: disable=import-outside-toplevel

    dash = AmazonDash()
    settings = dash.load_settings()
    sheet = Sheet(settings, "amazon_dash")
    row, event = sheet.get_last_event("white")
    print(event)


if __name__ == "__main__":  # pragma: no cover
    check()
