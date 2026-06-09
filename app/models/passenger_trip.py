from dataclasses import dataclass
from datetime import datetime
from app.utils import safe_float_parser, safe_date_parser


@dataclass
class PassengerTrip:
    passenger: str | None
    pickup: str | None
    dropoff: str | None
    society: str | None
    start_time: str | None
    site: str | None
    site: str | None
    price: float | None
    taxi: str | None
    date: datetime | None

    # completed: bool

    @classmethod
    def from_sheet_row(cls, row: dict):
        return cls(passenger=row.get("Fullname", ""),
                   pickup=row.get("Pickup", ""),
                   dropoff=row.get("Dropoff", ""),
                   start_time=row.get("Start Time", ""),
                   society=row.get("Society", ""),
                   site=row.get("Site", ""),
                   price=safe_float_parser(row.get("Price", "")),
                   date=safe_date_parser(row.get("Date", "")),
                   taxi=row.get("Taxi", ""))

