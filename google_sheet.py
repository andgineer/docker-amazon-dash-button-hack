import gspread
from gspread.exceptions import CellNotFound
from oauth2client.service_account import ServiceAccountCredentials
import datetime


CREDENTIALS_FILE_NAME = 'amazone-dash-private/amazone-dash-hack.json'
DOC_NAME = 'amazon_dash'
SETTINGS_SHEET_NAME = 'settings'
PRESS_SHEET_NAME = 'press'
EVENT_SHEET_NAME = 'event'
START_TIME_COL = 2 # column in event sheet with date-time of event start
END_TIME_COL = 3 # column in event sheet with date-time of event end
PARAMS = {
    'restart': { # Second button press in this interval do nothing (seconds). If zero - switched off.
        'name': 'restart',
        'default': 3*60,
    },
    'autoclose': { # After that period of time (seconds) button press will auto-close previuos unclosed interval with defaul length and start new one. If zero - switched off.
        'name': 'autoclose',
        'default': 3*60*60,
    },
    'default': { # Default length (seconds) for interval if auto-close (see restart parameter).
        'name': 'default',
        'default': 15*60,
    }
}
GDRIVE_TIME_FORMAT = '%d/%m/%Y %H:%M:%S'
SHEET_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Sheet:
    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE_NAME,
            ['https://spreadsheets.google.com/feeds'])
        gc = gspread.authorize(credentials)
        self.gdoc = gc.open(DOC_NAME)


    def press(self, button):
        press_sheet = self.gdoc.worksheet(PRESS_SHEET_NAME)
        press_sheet.insert_row([button, datetime.datetime.now().strftime(GDRIVE_TIME_FORMAT)], index=2)
        # index=2 - insert below header row


    def event(self, button):
        def load_params():
            settings_sheet = self.gdoc.worksheet(SETTINGS_SHEET_NAME)
            settings_list = settings_sheet.get_all_values()[1:]
            settings = {}
            for row in settings_list:
                button_name = row[0] # Button name in first column
                if not button_name in settings:
                    settings[button_name] = {}
                settings[button_name][row[1]] = row[2] # param name in second column and value in third
            if button not in settings:
                return {name: int(PARAMS[name]['default']) for name in PARAMS}
                print('no params for the button, use defaults')
            else:
                return {name: int(settings[button].get(PARAMS[name]['name'], PARAMS[name]['default'])) for name in PARAMS}

        def start_event(event_sheet):
            event_sheet.insert_row(
                [
                    button,
                    datetime.datetime.now().strftime(GDRIVE_TIME_FORMAT),
                    '',
                    '=(C{row}-B{row})'.format(row=2)
                ],
                index=2)

        def close_event(event_sheet, last_event, finish_time):
            event_sheet.update_cell(
                last_event.row, END_TIME_COL,
                finish_time
                )

        params = load_params()
        event_sheet = self.gdoc.worksheet(EVENT_SHEET_NAME)
        try:
            last_event = event_sheet.find(button)
        except CellNotFound as e:
            last_event = None
            print('first event for the button!')
        if last_event:
            last_start = datetime.datetime.strptime(event_sheet.cell(last_event.row, START_TIME_COL).value, SHEET_TIME_FORMAT)
            if event_sheet.cell(last_event.row, END_TIME_COL).value:
                last_end = datetime.datetime.strptime(event_sheet.cell(last_event.row, END_TIME_COL).value, SHEET_TIME_FORMAT)
            else:
                last_end = None
            if last_end and datetime.datetime.now() - last_end < datetime.timedelta(seconds=params['restart']):
                print('Button press ignored because previuos event closed and it is too early to start new one')
                return
            if datetime.datetime.now() - last_start < datetime.timedelta(seconds=params['restart']):
                print('Button press ignored because event in progress and it is too early to close it')
                return
            if not last_end:
                if datetime.datetime.now() - last_start > datetime.timedelta(seconds=params['autoclose']):
                    close_event(event_sheet, last_event, last_start + datetime.timedelta(seconds=params['default'])).strftime(GDRIVE_TIME_FORMAT)
                    print('Auto close previous event')
                else:
                    close_event(event_sheet, last_event, datetime.datetime.now().strftime(GDRIVE_TIME_FORMAT))
                    print('Close previous event')
                    return
        start_event(event_sheet)
        print('New event started')


if __name__ == '__main__':
    sheet = Sheet()
    sheet.press('white')
    sheet.event('white')