"""Register amazon dash (button) events in Google calendar using Google Calendar API """

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import httplib2
import datetime
import os


GCAL_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
GCAL_TIME_PARSE = '%Y-%m-%dT%H:%M:%SZ'

class Calendar(object):
    def __init__(self, settings):
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.tz = os.environ.get('TZ', 'Europe/Moscow')
        self.calendarId = self.settings['calendarId']
        #self.calendarId = self.get_calendar_id(name)

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
            'calendar',
            'v3',
            http=self.http
        )

    def get_calendar_id(self, name):
        """Does not work for some uncleare reasons.
        returns empty items.
        And if I access calendar 'primary' events created in some other calendar invisible for other accounts.
        So we have to specify calendarId implicitely and cannot find it by name.
        """
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            print(calendar_list)
            for calendar_list_entry in calendar_list['items']:
                print(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

    def start_event(self, summary):
        INSERT_EVENT_REQUEST = {
            'summary': summary,
            'description': 'Event created by amazon dash (button) click.',
            'start': {
                'dateTime': datetime.datetime.utcnow().strftime(GCAL_TIME_FORMAT),
                'timeZone': '{tz}'.format(tz=self.tz),
            },
            'end': {
                'dateTime': datetime.datetime.utcnow().strftime(GCAL_TIME_FORMAT),
                'timeZone': '{tz}'.format(tz=self.tz),
            },
        }
        event = self.service.events().insert(
            calendarId=self.calendarId, #'primary',
            body=INSERT_EVENT_REQUEST
        ).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    def get_last_event(self, summary):
        """
        :param summary: text to search
        :return:
        <id for close event>, [summary, start, end]
        """
        page_token = None
        while True:
            # we need only last event but do not see how to get just it from the API
            events = self.service.events().list(
                calendarId=self.calendarId, #'primary',
                timeMin=self.google_time_format(datetime.datetime.now() - datetime.timedelta(days=100)), # better limit than sorry
                q=summary,
                timeZone='UTC',
                orderBy="startTime",
                singleEvents=True,
                showDeleted=False,
                pageToken=page_token
            ).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                # very stupid - we have to skip to last page
                if len(events['items']) > 0:
                    event = events['items'][-1]
                    # from pprint import pprint
                    # pprint(events)
                    start = datetime.datetime.strptime(event['start']['dateTime'], GCAL_TIME_PARSE)
                    if event['start'] == event['end']:
                        return event['id'], [event['summary'], start]
                    else:
                        end = datetime.datetime.strptime(event['end']['dateTime'], GCAL_TIME_PARSE)
                        return event['id'], [event['summary'], start, end]
                return None, None

    def delete_event(self, event_id):
        self.service.events().delete(
            calendarId=self.calendarId, #'primary',
            eventId=event_id
        ).execute()

    def close_event(self, event_id, close_time):
        event = self.service.events().get(
            calendarId=self.calendarId, #'primary',
            eventId=event_id).execute()
        event['end'] = {
            'dateTime': close_time.strftime(GCAL_TIME_FORMAT),
            'timeZone': '{tz}'.format(tz=self.tz),
        }
        updated_event = self.service.events().update(
            calendarId=self.calendarId, #'primary',
            eventId=event_id,
            body=event
        ).execute()
        print(updated_event)

    def google_time_format(self, t):
        return t.strftime('%Y-%m-%dT%H:%M:%SZ')

    def google_now(self):
        return self.google_time_format(datetime.datetime.utcnow())

    def google_today(self):
        return self.google_time_format(
                    datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                )


if __name__ == "__main__":
    from amazon_dash import load_settings
    settings = load_settings()
    calendar = Calendar(settings)
    # while True:
    #     id, event = calendar.get_last_event('Google')
    #     if id:
    #         calendar.delete_event(id)
    #     else:
    #         break
    calendar.get_calendar_id('Anna')
    calendar.start_event('Google')
    print(calendar.get_last_event('Google'))
    id, event = calendar.get_last_event('Google')
    calendar.close_event(id, (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)))
    #calendar.action('white')