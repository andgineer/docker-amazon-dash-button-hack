"""
Action for OpenHAB item
http://demo.openhab.org:8080/doc/index.html
"""

import requests
import json


class OpenHab():
    def __init__(self, settings):
        self.settings = settings

    def press(self, action_params):
        """
        Gets current item state and changes it to opposite status.
        """
        base_url = '{path}/items/{item}'.format(
            path=action_params['path'],
            item=action_params['item'],
        )
        commands = action_params['command'].upper().split(';')
        if len(commands) != 2:
            print('\nWrong "command" setting in openhab action. Should be two openHAB commands separated by ";" ("ON;OFF" or "UP;DOWN"). Button press will switch between them.')

        state = requests.get(
            base_url + '/state',
            headers={'content-type': 'application/json'}
        )
        try:
            current_idx = commands.index(state.text.upper())
        except ValueError:
            print('Item {} now in state {}. But in "command" settings ({}) there is no such state.'.format(
                action_params['item'],
                state.text,
                action_params['command']
            ))
            return

        command_idx = (current_idx + 1) % 2  # switch between two states
        requests.post(
            base_url,
            data=json.dumps(commands[command_idx]),
            headers={'content-type': 'application/json'}
        )
