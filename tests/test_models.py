import pytest

from models import ButtonMacs
from pydantic import ValidationError


def test_valid_mac_addresses():
    valid_data = {
        "34:d2:70:a4:e0:50": "button1",
        "44:65:0d:c2:18:b5": "button2"
    }
    # This should not raise any error
    ButtonMacs(valid_data)


def test_invalid_mac_addresses():
    invalid_data_1 = {
        "34:d2:70:a4:e0:G0": "button1",  # Invalid character G
        "44:65:0d:c2:18:b5": "button2"
    }

    invalid_data_2 = {
        "344:d2:70:a4:e0:50": "button1",  # Extra character
        "44:65:0d:c2:18:b5": "button2"
    }

    invalid_data_3 = {
        "34:d2:70:a4:e0": "button1",  # Incomplete MAC
        "44:65:0d:c2:18:b5": "button2"
    }

    with pytest.raises(ValidationError):
        ButtonMacs(invalid_data_1)

    with pytest.raises(ValidationError):
        ButtonMacs(invalid_data_2)

    with pytest.raises(ValidationError):
        ButtonMacs(invalid_data_3)
