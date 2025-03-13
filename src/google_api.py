"""Google API class."""

from datetime import datetime
from functools import cached_property
from typing import Any, Optional, Union

import httplib2
from googleapiclient import discovery  # pyright: ignore [reportMissingImports]
from oauth2client.service_account import (
    ServiceAccountCredentials,  # pyright: ignore [reportMissingImports, reportMissingTypeStubs]
)

import models


class GoogleApi:
    """Google API class."""

    settings: models.Settings

    def __init__(self, settings: models.Settings, api: str, version: str) -> None:
        """Init."""
        self.settings = settings
        self.http = self.get_credentials_http()
        self.api = api
        self.version = version

    def get_credentials_http(self) -> httplib2.Http:
        """Get credentials for http."""
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.settings.credentials_file_name,
                [  # pyright: ignore [reportArgumentType]
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

        return credentials.authorize(httplib2.Http())

    def get_service(self, api: str, version: str) -> Any:
        if not self.http:
            raise ValueError(f"Cannot get service `{self.api}`: Google API is not authorized.")
        return discovery.build(api, version, http=self.http)

    @cached_property
    def service(self) -> Any:  # do not use discovery.Resource as workaround for mypy
        """Get service."""
        return self.get_service(self.api, self.version)

    def get_last_event(
        self,
        summary: str,
    ) -> tuple[Optional[Union[int, str]], Optional[list[Any]]]:
        """Get last event."""
        raise NotImplementedError

    def start_event(self, summary: str) -> None:
        """Start event."""
        raise NotImplementedError

    def close_event(self, event_id: Union[int, str], close_time: datetime) -> None:
        """Close event."""
        raise NotImplementedError
