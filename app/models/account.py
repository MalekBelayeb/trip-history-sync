from dataclasses import dataclass


@dataclass
class Account:
    login: str | None
    password: str | None
    name: str | None
    type: str | None
    taxi_number: str | None
