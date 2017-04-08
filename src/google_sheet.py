"""Register amazon dash (button) events in Google spreadsheet using Google Sheet API """

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import httplib2
import datetime


GSHEET_TIME_FORMAT = '%d/%m/%Y %H:%M:%S'


class Sheet(object):
    def __init__(self, settings, name, press_sheet='press', event_sheet='event'):
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.drive_service = self.get_drive_service()
        self.spreadSheetId = self.get_file_id(name)
        self.get_sheets()
        self.press_sheet = press_sheet
        self.event_sheet = event_sheet

    def get_last_event(self, summary):
        """
        :param summary: text to search
        :return:
        <id for close event>, [summary, start, end]
        """
        row, event = self.find_last_row(sheet=self.event_sheet, search_string=summary)
        if event:
            for col in range(1, len(event)):
                event[col] = self.from_serial_time(event[col])
            return row, event
        else:
            return None, None

    def start_event(self, summary):
        self.insert_row(sheet=self.event_sheet)
        self.copy_row_formatting(sheet=self.event_sheet)
        self.update_cells(
            sheet=self.event_sheet,
            values=[summary, datetime.datetime.now().strftime(GSHEET_TIME_FORMAT)])

    def close_event(self, event_row, close_time):
        """row 0-based"""
        self.update_cells(
            sheet=self.event_sheet,
            row=event_row,
            col=2,
            values=[close_time.strftime(GSHEET_TIME_FORMAT), '=C{row}-B{row}'.format(row=event_row + 1)])

    def press(self, summary):
        self.insert_row(sheet=self.press_sheet)
        self.copy_row_formatting(sheet=self.press_sheet)
        self.update_cells(sheet=self.press_sheet, values=[summary, datetime.datetime.now().strftime(GSHEET_TIME_FORMAT)])

    def get_file_id(self, name):
        """
        :param name: file name
        :return: file id
        """
        page_token = None
        while True:
            # Full blown page iteration from API doc
            # but in fact we will get exactly one or no one file
            response = self.drive_service.files().list(
                q="name='{}'".format(name),
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()
            for file in response.get('files', []):
                return file.get('id')
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def find_last_row(self, sheet, search_string, search_in_col=0):
        """ Very stupid implementation, but:
                The Sheets API v4 does not currently have a direct equivalent for the Sheets API v3 structured queries.
                However, you can retrieve the relevant data and sort through it as needed in your application.
        """
        ROWS_TO_FETCH = 1000 # well, we have to stop somewhere and 1000 looks as good as any other limit
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
        else:
            return None, None

    def get_credentials_http(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.settings['credentialsFileName'],
            [
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.metadata.readonly'
            ]
        )
        return credentials.authorize(httplib2.Http())

    def get_service(self):
        return discovery.build(
            'sheets',
            'v4',
            http=self.http,
            discoveryServiceUrl=('https://sheets.googleapis.com/$discovery/rest?version=v4')
        )

    def get_drive_service(self):
        return discovery.build('drive', 'v3', http=self.http)

    def get_sheets(self):
        request = self.service.spreadsheets().get(
            spreadsheetId=self.spreadSheetId,
            ranges=[],
            includeGridData=False)
        sheets = request.execute()['sheets']
        self.sheets = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}

    def update_cells(self, sheet, values, row=1, col=0):
        """row and col 0-based"""
        request = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadSheetId,
            range='{sheet}!{col}{row}:{last_col}'.format(
                sheet=sheet, col=chr(ord('A') + col), row=row + 1, last_col=chr(ord('A') + col + len(values) - 1)),
            valueInputOption='USER_ENTERED',
            body={
                "majorDimension": 'ROWS',
                "values": [
                    values
                ],
            })
        return request.execute()

    def append_row(self, sheet, values, row=1):
        """row 0-based"""
        request = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadSheetId,
            range='{sheet}!A{row}:{last_col}'.format(
                sheet=sheet, row=row + 1, last_col=chr(ord('A') + len(values) - 1)),
            valueInputOption='RAW', #'USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={
                "majorDimension": 'ROWS',
                "values": [
                    values
                ]
            }
        )

    def insert_row(self, sheet, after=1):
        INSERT_ROW_REQUEST = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": self.sheets[sheet],
                            "dimension": "ROWS",
                            "startIndex": after,
                            "endIndex": after + 1
                        },
                        "inheritFromBefore": False
                    }
                },
            ],
        }
        request = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadSheetId,
            body=INSERT_ROW_REQUEST
        )
        return request.execute()

    def copy_row_formatting(self, sheet, copy_from=2, copy_to=1):
        COPY_FORMATTING_REQUEST = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": self.sheets[sheet],
                            "startRowIndex": copy_from - 1,
                            "endRowIndex": copy_from,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1000
                        },
                        "destination": {
                            "sheetId": self.sheets[sheet],
                            "startRowIndex": copy_to - 1,
                            "endRowIndex": copy_to,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1000
                        },
                        "pasteType": "PASTE_FORMAT",
                        "pasteOrientation": "NORMAL"
                    }
                }
            ]
        }
        request = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadSheetId,
            body=COPY_FORMATTING_REQUEST
        )
        return request.execute()

    def get_rows(self, sheet, row=1, rows=1, cols=3):
        """row 0-based"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadSheetId,
            range='{sheet}!A{row}:{last_col}{last_row}'.format(
                sheet=sheet, row=row + 1, last_col=chr(ord('A') + cols - 1), last_row=row + rows - 1),
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        values = result.get('values', [])
        return values

    def from_serial_time(self, serial):
        """Converts google 'serial number' date-time to datetime """
        return datetime.datetime(year=1899, month=12, day=30) + datetime.timedelta(days=serial)


if __name__ == "__main__":
    from amazon_dash import load_settings
    settings = load_settings()
    sheet = Sheet(settings, 'amazon_dash')
    row, event = sheet.get_last_event('white')
    print(event)
