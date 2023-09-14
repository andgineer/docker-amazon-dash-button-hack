"""Register Amazon Dash Button events in Google Calendar using Google Calendar API """

import datetime
import os
import time

import dateutil.parser

from google_api import GoogleApi

# GCAL_TIME_PARSE = '%Y-%m-%dT%H:%M:%S%z'


class Calendar(GoogleApi):
    def __init__(self, settings, calendar_id):
        super().__init__(settings, api="calendar", version="v3")
        self.tz = os.environ.get("TZ", "Europe/Moscow")
        self.calendarId = calendar_id

    def get_calendar_id(self, name):
        """Does not work for some unclear reasons.
        returns empty items.
        And if I access calendar 'primary' events created in some other calendar invisible for other accounts.
        So we have to specify calendarId implicitly and cannot find it by name.
        """
        page_token = None
        while True:
            calendar_list = self.service().calendarList().list(pageToken=page_token).execute()
            print(calendar_list)
            for calendar_list_entry in calendar_list["items"]:
                print(calendar_list_entry["summary"])
            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break

    def parse_time(self, s):
        return dateutil.parser.parse(s)

    def time_to_str(self, t):
        GCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        tz = -time.timezone / 60 / 60 * 100
        # todo that is incorrect - you need minutes after ':' not hours % 100
        # so h = int(- time.timezone / 60 / 60)
        # m = abs(time.timezone / 60) - h * 60
        s = t.strftime(GCAL_TIME_FORMAT) + "%+03d:%02d" % (tz / 100, abs(tz % 100))
        return s

    def start_event(self, summary):
        INSERT_EVENT_REQUEST = {
            "summary": summary,
            "description": "Event created by amazon dash (button) click.",
            "start": {
                "dateTime": self.time_to_str(datetime.datetime.now()),
                #'timeZone': '{tz}'.format(tz=self.tz),
            },
            "end": {
                "dateTime": self.time_to_str(datetime.datetime.now()),
                #'timeZone': '{tz}'.format(tz=self.tz),
            },
        }
        event = (
            self.service()
            .events()
            .insert(calendarId=self.calendarId, body=INSERT_EVENT_REQUEST)  #'primary',
            .execute()
        )
        # print('Calendar event created: %s' % (event.get('htmlLink')))

    def get_last_event(self, summary):
        """
        :param summary: text to search
        :return:
        <id for close event>, [summary, start, end]
        """
        page_token = None
        while True:
            # we need only last event but do not see how to get just it from the API
            events = (
                self.service()
                .events()
                .list(
                    calendarId=self.calendarId,  #'primary',
                    timeMin=self.google_time_format(
                        datetime.datetime.now() - datetime.timedelta(days=100)
                    ),  # better limit than sorry
                    q=summary,
                    # timeZone='UTC',
                    orderBy="startTime",
                    singleEvents=True,
                    showDeleted=False,
                    pageToken=page_token,
                )
                .execute()
            )
            page_token = events.get("nextPageToken")
            if not page_token:
                # very stupid - we have to skip to last page
                if len(events["items"]) > 0:
                    event = events["items"][-1]
                    # from pprint import pprint
                    # pprint(events)
                    start = self.parse_time(event["start"]["dateTime"])
                    if event["start"] == event["end"]:
                        return event["id"], [event["summary"], start]
                    else:
                        end = self.parse_time(event["end"]["dateTime"])
                        return event["id"], [event["summary"], start, end]
                return None, None

    def delete_event(self, event_id):
        self.service().events().delete(
            calendarId=self.calendarId, eventId=event_id  #'primary',
        ).execute()

    def close_event(self, event_id, close_time):
        event = (
            self.service()
            .events()
            .get(calendarId=self.calendarId, eventId=event_id)  #'primary',
            .execute()
        )
        event["end"] = {
            "dateTime": self.time_to_str(close_time),
            #'timeZone': '{tz}'.format(tz=self.tz),
        }
        updated_event = (
            self.service()
            .events()
            .update(calendarId=self.calendarId, eventId=event_id, body=event)  #'primary',
            .execute()
        )
        # print(updated_event)

    def google_time_format(self, t):
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def google_now(self):
        return self.google_time_format(datetime.datetime.now())

    def google_today(self):
        return self.google_time_format(
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )


if __name__ == "__main__":  # pragma: no cover
    from amazon_dash import load_settings

    settings = load_settings()
    calendar = Calendar(settings, settings["actions"]["white"]["actions"][1]["calendar_id"])
    # while True:
    #     id, event = calendar.get_last_event('Google')
    #     if id:
    #         calendar.delete_event(id)
    #     else:
    #         break
    calendar.start_event("Google")
    print(calendar.get_last_event("Google"))
    id, event = calendar.get_last_event("Google")
    calendar.close_event(id, (datetime.datetime.now() + datetime.timedelta(minutes=5)))
