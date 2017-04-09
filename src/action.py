"""
Registers events from amazon dash (button).
Supports google sheet (google_sheet.py), google calendar (google_calendar.py) and ifttt (ifttt.py)
"""
from google_sheet import Sheet
from google_calendar import Calendar
from ifttt import Ifttt
import datetime
import copy


class Action(object):
    def __init__(self, settings):
        self.settings = settings
        self.actions = settings['actions']

    def preprocess_actions(self, button, actions):
        """
        Add summary (with button name value) if there is no one.
        Substitutes {button} with button name in parameters.
        """
        def subst(s):
            return s.format(button=button)
        actions = copy.deepcopy(actions)
        for action in actions:
            if 'summary' not in action:
                action['summary'] = button
            for param in action:
                if isinstance(action[param], str):
                    action[param] = subst(action[param])
        return actions

    def action(self, button):
        """Registers event from the button"""
        ACTION_HANDLERS = {
            'sheet': self.sheet_action,
            'calendar': self.calendar_action,
            'ifttt': self.ifttt_action,
        }
        if button in self.actions:
            actions = self.actions[button]['actions']
        else:
            actions = self.actions['__DEFAULT__']['actions']
        actions = self.preprocess_actions(button, actions)
        for act in actions:
            print('Event for {}:'.format(act['type']))
            ACTION_HANDLERS[act['type']](button, act)

    def ifttt_action(self, button, action_params):
        ifttt = Ifttt(self.settings)
        ifttt.press(
            action_params['summary'],
            action_params.get('value1', ''),
            action_params.get('value2', ''),
            action_params.get('value3', '')
        )

    def calendar_action(self, button, action_params):
        calendar = Calendar(self.settings, action_params['calendar_id'])
        self.event(calendar, action_params)

    def sheet_action(self, button, action_params):
        sheet = Sheet(
            self.settings,
            action_params['name'],
            press_sheet=action_params['press_sheet'],
            event_sheet=action_params['event_sheet']
        )
        sheet.press(action_params['summary'])
        self.event(sheet, action_params)

    def event(self, target, action_params):
        """Event registration common logic"""
        last_event_row, last_event = target.get_last_event(action_params['summary'])
        if last_event:
            last_start = last_event[1]
            if len(last_event) > 2:
                last_end = last_event[2]
            else:
                last_end = None
            nowtz = datetime.datetime.now(last_start.tzinfo)
            if last_end and abs(nowtz - last_end) < datetime.timedelta(seconds=action_params['restart']):
                print('Button press ignored because previuos event closed and it is too early to start new one')
                return
            if nowtz - last_start < datetime.timedelta(seconds=action_params['restart']):
                print('Button press ignored because event in progress and it is too early to close it')
                return
            if not last_end:
                if abs(nowtz - last_start) > datetime.timedelta(seconds=action_params['autoclose']):
                    target.close_event(
                        last_event_row,
                        (last_start + datetime.timedelta(seconds=action_params['default'])))
                    print('Auto close previous event')
                else:
                    target.close_event(last_event_row, datetime.datetime.now())
                    print('Close previous event')
                    return
        target.start_event(action_params['summary'])
        print('New event started')


if __name__ == "__main__":
    from amazon_dash import load_settings
    settings = load_settings()
    action = Action(settings)
    action.action('white')