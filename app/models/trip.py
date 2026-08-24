from dataclasses import dataclass
from app.models import PassengerTrip


@dataclass
class Trip:
    id: str | None
    site: str
    society: str | None
    site: str | None
    start_time: str | None
    date: str | None
    taxi: str | None
    price: float | None
    trip_passengers: list[PassengerTrip] | None
