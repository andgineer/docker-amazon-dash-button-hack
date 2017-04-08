"""Register amazon dash (button) events IFTTT Makers API """
import requests
import json


class Ifttt():
    def __init__(self, settings):
        self.settings = settings
        self.key_file = self.load_key()
        self.key = self.key_file['key']

    def load_key(self):
        with open(self.settings['iftttKeyFileName'], 'r') as key_file:
            return json.loads(key_file.read())

    def press(self, summary):
        payload = {
            'value1': 'hello1',
            'value2': 'hello2',
            'value3': 'hello3'
        }
        requests.post(
            'https://maker.ifttt.com/trigger/{event}/with/key/{key}'.format(
                event=summary,
                key=self.key
            ),
            data=json.dumps(payload),
            headers={'content-type': 'application/json'}
        )


if __name__ == "__main__":
    from amazon_dash import load_settings
    settings = load_settings()
    ifttt = Ifttt(settings)
    ifttt.press('white_amazon_dash')