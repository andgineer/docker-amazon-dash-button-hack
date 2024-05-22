from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, RootModel, TypeAdapter, constr, model_validator  # pyright: ignore [reportMissingImports]

BOUNCE_DELAY = 5


class TimeSummary(BaseModel):
    """Summary for a time interval."""

    summary: str
    before: Optional[str] = None
    image: str


class DashBoardAbsent(BaseModel):
    """Absent images."""

    summary: str
    image_grid: str
    image_plot: str


class DashboardItem(BaseModel):
    """Dashboard item."""

    summary: str
    empty_image: str
    absent: List[DashBoardAbsent]


SummaryType = Union[str, List[TimeSummary]]


class CustomBaseModel(BaseModel):
    """Base model with custom validators."""

    @model_validator(mode="before")
    def check_summary_type_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check summary type fields."""
        for field, value in values.items():
            expected_type = cls.__annotations__.get(field)
            if expected_type is SummaryType and isinstance(value, list):
                assert (
                    len(value) > 0
                ), """summary param must be string or array like [{"summary":"summary1", "before":"10:00:00"}, {"summary": "summary2", "before":"19:00:00"}, ...]"""
        return values


class SheetAction(CustomBaseModel):
    """Action for a google sheet."""

    type: Literal["sheet"]
    summary: Optional[SummaryType] = None
    name: str
    press_sheet: str
    event_sheet: str
    restart: int
    autoclose: int
    default: int


class CalendarAction(CustomBaseModel):
    """Action for a google calendar."""

    type: Literal["calendar"]
    summary: Optional[SummaryType] = None
    calendar_id: str
    dashboard: Optional[str] = None
    restart: int
    autoclose: int
    default: int


class IftttAction(CustomBaseModel):
    """Action for a IFTTT."""

    type: Literal["ifttt"]
    summary: Optional[SummaryType] = None
    value1: str = ""
    value2: str = ""
    value3: str = ""


class OpenhabAction(CustomBaseModel):
    """Action for a OpenHab.""" ""

    type: Literal["openhab"]
    summary: Optional[SummaryType] = None
    path: str
    item: str
    command: str


ActionItem = Union[SheetAction, CalendarAction, IftttAction, OpenhabAction]
ActionItemLoad = TypeAdapter(ActionItem).validate_python


class EventActions(CustomBaseModel):
    """Actions for an event."""

    # todo: flag that this is button event to have other types of events
    summary: SummaryType
    actions: List[ActionItem]


class Settings(BaseModel):
    """Settings for the application.""" ""

    latitude: str
    longitude: str
    credentials_file_name: str
    ifttt_key_file_name: str
    openweathermap_key_file_name: str
    images_folder: str
    bounce_delay: int = BOUNCE_DELAY
    dashboards: Dict[str, DashboardItem]
    events: Dict[str, EventActions]


MACAddress = constr(pattern="^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")
ButtonMacs = RootModel[Dict[MACAddress, str]]  # type: ignore
