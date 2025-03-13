"""Action for OpenHAB item.

http://demo.openhab.org:8080/doc/index.html
"""

import json

import requests

import models


class OpenHab:
    """Action for OpenHAB item."""

    def __init__(self, settings: models.Settings) -> None:
        """Init."""
        self.settings = settings

    def press(self, action_params: models.OpenhabAction) -> None:
        """Get current item state and changes it to opposite status."""
        base_url = f"{action_params.path}/items/{action_params.item}"
        commands = action_params.command.upper().split(";")
        expected_command_count = 2
        if len(commands) != expected_command_count:
            print(
                '\nWrong "command" setting in openhab action. '
                'Should be two openHAB commands separated by ";" ("ON;OFF" or "UP;DOWN"). '
                "Button press will switch between them.",
            )
            return

        state = requests.get(
            f"{base_url}/state",
            headers={"content-type": "application/json"},
            timeout=5,
        )
        try:
            current_idx = commands.index(state.text.upper())
        except ValueError:
            print(
                f"Item {action_params.item} now in state {state.text}. "
                f'But in "command" settings ({action_params.command}) there is no such state.',
            )
            return

        command_idx = (current_idx + 1) % 2  # switch between two states
        requests.post(
            base_url,
            data=json.dumps(commands[command_idx]),
            headers={"content-type": "application/json"},
            timeout=5,
        )
