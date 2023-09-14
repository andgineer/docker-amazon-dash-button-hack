"""Google API class."""
from typing import Any, Dict, Optional

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApi:
    """Google API class."""

    def __init__(self, settings: Dict[str, Any], api: str, version: str) -> None:
        """Init."""
        self.settings = settings
        self.http = self.get_credentials_http()
        self._service = self.get_service(api=api, version=version)

    def get_credentials_http(self) -> Optional[httplib2.Http]:
        """Get credentials for http."""
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.settings["credentials_file_name"],
                [
                    "https://www.googleapis.com/auth/calendar",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.metadata.readonly",
                ],
            )
        except Exception as e:
            error_message = (
                "\n!!!!! Cannot get authorization from google API. "
                f"Maybe the API Key is invalid ({self.settings['credentials_file_name']}):\n\n{e}"
            )
            print(error_message)

            return None
        return credentials.authorize(httplib2.Http())

    def get_service(self, api: str, version: str) -> Optional[discovery.Resource]:
        """Get service."""
        return discovery.build(api, version, http=self.http) if self.http else None

    def service(self) -> Optional[discovery.Resource]:
        """Get service."""
        if self._service:
            return self._service
        print("!" * 5 + " Google API service undefined.")
        return None
