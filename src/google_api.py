"""Google API class."""

from datetime import datetime
from functools import cached_property
from typing import Any

from google.oauth2 import service_account
from googleapiclient import discovery

import models


class GoogleApi:
    """Google API class."""

    settings: models.Settings

    def __init__(self, settings: models.Settings, api: str, version: str) -> None:
        """Init."""
        self.settings = settings
        self.credentials = self.get_credentials()
        self.api = api
        self.version = version

    def get_credentials(self) -> service_account.Credentials:
        """Get credentials for http."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.settings.credentials_file_name,
                scopes=[
                    "https://www.googleapis.com/auth/calendar",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.metadata.readonly",
                ],
            )
        except Exception as e:
            error_message = (
                f"\n!!!!! Cannot get authorization from google API. "
                f"Maybe the API Key is invalid ({self.settings.credentials_file_name}):\n\n{e}"
            )
            raise ValueError(error_message) from e

        return credentials

    def get_service(self, api: str, version: str) -> Any:
        if not self.credentials:
            raise ValueError(f"Cannot get service `{self.api}`: Google API is not authorized.")
        return discovery.build(api, version, credentials=self.credentials)

    @cached_property
    def service(self) -> Any:  # do not use discovery.Resource as workaround for pyrefly
        """Get service."""
        return self.get_service(self.api, self.version)

    def get_last_event(
        self,
        summary: str,
    ) -> tuple[int | str | None, list[Any] | None]:
        """Get last event."""
        raise NotImplementedError

    def start_event(self, summary: str) -> None:
        """Start event."""
        raise NotImplementedError

    def close_event(self, event_id: int | str, close_time: datetime) -> None:
        """Close event."""
        raise NotImplementedError
