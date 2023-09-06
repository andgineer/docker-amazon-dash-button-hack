import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApi(object):
    def get_credentials_http(self):
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
            print(
                "\n"
                + "!" * 5
                + " Cannot get authorization from google API. May be google API Key is invalid ({}):\n\n{}".format(
                    self.settings["credentials_file_name"], e
                )
            )
            return None
        return credentials.authorize(httplib2.Http())

    def get_service(self, api, version):
        if self.http:
            return discovery.build(api, version, http=self.http)
        else:
            return None

    def service(self):
        if self._service:
            return self._service
        else:
            print("!" * 5 + " Google API service undefined.")
