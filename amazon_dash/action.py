"""
Registers events from amazon dash (button).
Supports google sheet (google_sheet.py), google calendar (google_calendar.py) and ifttt (ifttt.py)
"""
from google_sheet import Sheet
from google_calendar import Calendar
from ifttt import Ifttt
from openhab import OpenHab
from datetime import datetime, timedelta
import copy
import collections


class Action(object):
    def __init__(self, settings):
        self.settings = settings
        self.actions = settings['actions']

    def set_summary_by_time(self, button_actions):
        """
        :param button_actions:
        :return:
        if summary of any action in button_actions is a list, then select only one summary from the list
        in accordance with the current time
        """
        for action in button_actions:
            if isinstance(action['summary'], list):
                assert len(action['summary']) > 0, '''summary param must be string or array like
        [{"summary":"summary1", "before":"10:00:00"}, {"summary": "summary2", "before":"19:00:00"}, ...]'''
                time = datetime.now()
                for interval_idx, interval in enumerate(action['summary']):
                    if 'before' in interval:
                        time_parts = interval['before'].split(':')
                        try:
                            assert len([i for i in time_parts if 0 <= int(i) < 60]) == 3, \
                                'Before param ({}) should be "HH:MM:SS", for example 10:00:00.'.format(interval['before'])
                        except ValueError:
                            raise Exception('Between ":" in "before" param should be numbers.')
                        interval_end_parts = [int(s) for s in time_parts]
                        interval_end = time.replace(hour=interval_end_parts[0], minute=interval_end_parts[1], second=interval_end_parts[2])
                        if time < interval_end:
                            action['summary'] = interval['summary']
                            break
                else:
                    action['summary'] = interval['summary']
        return button_actions

    def preprocess_actions(self, button, button_settings):
        """
        Add summary (with button name value) if there is no one.
        Substitutes {button} with button name in parameters.
        """
        def subst(param):
            if isinstance(param, str):
                return param.format(button=button)
            if isinstance(param, collections.Mapping):
                result = {}
                for item in param:
                    result[item] = subst(param[item])
                return result
            if isinstance(param, collections.Iterable):
                result = []
                for item in param:
                    result.append(subst(item))
                return result
            return param
        actions = copy.deepcopy(button_settings['actions'])
        for action in actions:
            if 'summary' not in action:
                if 'summary' in button_settings:
                    action['summary'] = button_settings['summary']
                else:
                    action['summary'] = button
            for param in action:
                action[param] = subst(action[param])
        print(actions)
        return actions

    def action(self, button, dry_run=False):
        """Registers event from the button"""
        ACTION_HANDLERS = {
            'sheet': self.sheet_action,
            'calendar': self.calendar_action,
            'ifttt': self.ifttt_action,
            'openhab': self.openhab_action,
        }
        if button in self.actions:
            button_settings = self.actions[button]
        else:
            button_settings = self.actions['__DEFAULT__']
        actions = self.preprocess_actions(button, button_settings)
        actions = self.set_summary_by_time(actions)
        for act in actions:
            print('Event for {}: ({})'.format(act['type'], act))
            if not dry_run:
                try:
                    ACTION_HANDLERS[act['type']](button, act)
                except Exception as e:
                    print('!'*5, 'Event handling error:\n{}'.format(e))

    def ifttt_action(self, button, action_params):
        ifttt = Ifttt(self.settings)
        ifttt.press(
            action_params['summary'],
            action_params.get('value1', ''),
            action_params.get('value2', ''),
            action_params.get('value3', '')
        )

    def openhab_action(self, button, action_params):
        openhab = OpenHab(self.settings)
        openhab.press(action_params)

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
            nowtz = datetime.now(last_start.tzinfo)
            if last_end and abs(nowtz - last_end) < timedelta(seconds=action_params['restart']):
                print('Button press ignored because previuos event closed and it is too early to start new one')
                return
            if nowtz - last_start < timedelta(seconds=action_params['restart']):
                print('Button press ignored because event in progress and it is too early to close it')
                return
            if not last_end:
                if abs(nowtz - last_start) > timedelta(seconds=action_params['autoclose']):
                    target.close_event(
                        last_event_row,
                        (last_start + timedelta(seconds=action_params['default'])))
                    print('Auto close previous event')
                else:
                    target.close_event(last_event_row, datetime.now())
                    print('Close previous event')
                    return
        target.start_event(action_params['summary'])
        print('New event started')

