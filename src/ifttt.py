"""Register Amazon Dash Button events in IFTTT Maker Webhook.

https://ifttt.com/maker_webhooks
"""
import json
from typing import Any, Dict

import requests
from requests import RequestException


class Ifttt:
    """Register Amazon Dash Button events in IFTTT Maker Webhook."""

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Init."""
        self.settings = settings
        self.key_file = self.load_key()
        self.key = self.key_file["key"]

    def load_key(self) -> Dict[str, Any]:
        """Load IFTTT key from file."""
        with open(self.settings["ifttt_key_file_name"], "r", encoding="utf-8-sig") as key_file:
            return json.loads(key_file.read())

    def press(self, summary: str, v1: str, v2: str, v3: str) -> None:
        """Register event in IFTTT."""
        payload = {"value1": v1, "value2": v2, "value3": v3}
        # todo urlencode event string
        url = f"https://maker.ifttt.com/trigger/{summary}/with/key/{self.key}"
        try:
            result = requests.post(
                url,
                data=json.dumps(payload),
                headers={"content-type": "application/json"},
                timeout=5,
            )
            if result.status_code != 200:
                print("*" * 10, "IFTTT error:\n", url, "\n", result)
        except RequestException as e:
            print("*" * 10, "IFTTT request fail:\n", url, "\n", e)


if __name__ == "__main__":  # pragma: no cover
    from amazon_dash import load_settings

    settings = load_settings()
    ifttt = Ifttt(settings)
    ifttt.press("white_amazon_dash", "1", "2", "3")
