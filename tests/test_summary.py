import pytest
from pydantic import ValidationError
from models import EventActions


def test_valid_input():
    # Valid single string summary input
    valid_data_1 = {
        "event_type": "button",
        "summary": "A simple summary",
        "actions": [{
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900
        }]
    }

    # Valid list type summary input
    valid_data_2 = {
        "event_type": "button",
        "summary": [{"summary": "summary1", "before": "10:00:00", "image": "morning.png"}],
        "actions": [{
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900
        }]
    }

    assert EventActions(**valid_data_1)
    assert EventActions(**valid_data_2)


def test_invalid_input():
    # Invalid empty list summary input
    invalid_data = {
        "event_type": "button",
        "summary": [],
        "actions": [{
            "type": "sheet",
            "name": "amazon_dash",
            "press_sheet": "press",
            "event_sheet": "event",
            "restart": 15,
            "autoclose": 10800,
            "default": 900
        }]
    }

    with pytest.raises(ValidationError) as excinfo:
        EventActions(**invalid_data)

    assert "summary param must be string" in str(excinfo.value)


# Then run the tests
test_valid_input()
test_invalid_input()
