"""Register Amazon Dash Button events in Google Calendar using Google Calendar API."""

import datetime
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import dateutil.parser

from google_api import GoogleApi

# GCAL_TIME_PARSE = '%Y-%m-%dT%H:%M:%S%z'


class Calendar(GoogleApi):
    """Google Calendar API wrapper."""

    def __init__(self, settings: Dict[str, Any], calendar_id: str) -> None:
        """Init."""
        super().__init__(settings, api="calendar", version="v3")
        self.tz = os.environ.get("TZ", "Europe/Moscow")
        self.calendarId = calendar_id

    def get_calendar_id(self, name: str) -> Optional[str]:
        """Get ID of the calendar named as `name`.

        Does not work for some unclear reasons.
        returns empty `items` array in response.

        And if I access calendar 'primary' events created in some other calendar invisible for other accounts.
        So we have to specify calendarId implicitly and cannot find it by name.
        """
        page_token = None
        while True:
            calendar_list = self.service().calendarList().list(pageToken=page_token).execute()
            print("Calendar page:", calendar_list)
            if ids := [
                item["id"] for item in calendar_list.get("items", []) if item["summary"] == name
            ]:
                return ids[0]  # type: ignore
            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break
        return None

    def parse_time(self, s: str) -> datetime.datetime:
        """Parse Google Calendar time format to datetime."""
        return dateutil.parser.parse(s)

    def time_to_str(self, t: datetime.datetime) -> str:
        """Convert datetime to Google Calendar time format."""
        GCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        tz_minutes = -time.timezone // 60
        tz_hours, tz_minutes = divmod(tz_minutes, 60)
        return f"{t.strftime(GCAL_TIME_FORMAT)}{tz_hours:+03d}:{abs(tz_minutes):02d}"

    def start_event(self, summary: str) -> None:
        """Start event in Google Calendar."""
        INSERT_EVENT_REQUEST = {
            "summary": summary,
            "description": "Event created by amazon dash (button) click.",
            "start": {
                "dateTime": self.time_to_str(datetime.datetime.now()),
                # 'timeZone': '{tz}'.format(tz=self.tz),
            },
            "end": {
                "dateTime": self.time_to_str(datetime.datetime.now()),
                # 'timeZone': '{tz}'.format(tz=self.tz),
            },
        }
        _ = (
            self.service()
            .events()
            .insert(calendarId=self.calendarId, body=INSERT_EVENT_REQUEST)  # 'primary',
            .execute()
        )
        # print('Calendar event created: %s' % (event.get('htmlLink')))

    def get_last_event(self, summary: str) -> Tuple[Optional[str], Optional[List[Any]]]:
        """Get last event from Google Calendar.

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
                    calendarId=self.calendarId,  # 'primary',
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
                    end = self.parse_time(event["end"]["dateTime"])
                    return event["id"], [event["summary"], start, end]
                return None, None

    def delete_event(self, event_id: str) -> None:
        """Delete event from Google Calendar."""
        self.service().events().delete(
            calendarId=self.calendarId, eventId=event_id  # 'primary',
        ).execute()

    def close_event(self, event_id: Union[int, str], close_time: datetime.datetime) -> None:
        """Close event in Google Calendar."""
        event = (
            self.service()
            .events()
            .get(calendarId=self.calendarId, eventId=event_id)  # 'primary',
            .execute()
        )
        event["end"] = {
            "dateTime": self.time_to_str(close_time),
            # 'timeZone': '{tz}'.format(tz=self.tz),
        }
        _ = (
            self.service()
            .events()
            .update(calendarId=self.calendarId, eventId=event_id, body=event)  # 'primary',
            .execute()
        )
        # print(updated_event)

    def google_time_format(self, t: datetime.datetime) -> str:
        """Convert datetime to Google Calendar time format."""
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def google_now(self) -> str:
        """Get current time in Google Calendar time format."""
        return self.google_time_format(datetime.datetime.now())

    def google_today(self) -> str:
        """Get today's date in Google Calendar time format."""
        return self.google_time_format(
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )


if __name__ == "__main__":  # pragma: no cover
    from amazon_dash import load_settings

    settings = load_settings()
    calendar = Calendar(settings, settings["actions"]["white"]["actions"][1]["calendar_id"])
    calendar.get_calendar_id("Anna")
    # while True:
    #     id, event = calendar.get_last_event('Google')
    #     if id:
    #         calendar.delete_event(id)
    #     else:
    #         break
    # calendar.start_event("Google")
    # print(calendar.get_last_event("Google"))
    # id, event = calendar.get_last_event("Google")
    # calendar.close_event(id, (datetime.datetime.now() + datetime.timedelta(minutes=5)))
