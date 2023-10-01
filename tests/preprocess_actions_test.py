from action import Action

ACTIONS = {
    "summary": [
        {"summary": "Morning work-out", "before": "12:00:00", "image": "morning.png"},
        {"summary": "Physiotherapy", "image": "evening2.png"},
    ],
    "actions": [
        {
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
        },
        {
            "type": "calendar",
            "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
            "dashboard": "anna_work_out",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
        },
        {
            "type": "ifttt",
            "summary": "{button}_amazon_dash",
            "value1": "",
            "value2": "",
            "value3": "",
        },
    ],
}


def test_preprocess_actions():
    action = Action({"events": []})
    assert action.preprocess_actions("white", ACTIONS) == [
        {
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
            "summary": [
                {"summary": "Morning work-out", "before": "12:00:00", "image": "morning.png"},
                {"summary": "Physiotherapy", "image": "evening2.png"},
            ],
        },
        {
            "type": "calendar",
            "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
            "dashboard": "anna_work_out",
            "restart": 15,
            "autoclose": 10800,
            "default": 900,
            "summary": [
                {"summary": "Morning work-out", "before": "12:00:00", "image": "morning.png"},
                {"summary": "Physiotherapy", "image": "evening2.png"},
            ],
        },
        {
            "type": "ifttt",
            "summary": "white_amazon_dash",
            "value1": "",
            "value2": "",
            "value3": "",
        },
    ]
