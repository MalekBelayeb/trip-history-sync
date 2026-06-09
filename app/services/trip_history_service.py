from collections import defaultdict
from datetime import datetime, date

from app.models import PassengerTrip, Trip
from .google_sheet_reader_service import GoogleSheetReaderService


class TripHistoryService:
    def __init__(self, google_sheet_reader_service: GoogleSheetReaderService):
        self.google_sheet_reader_service = google_sheet_reader_service

    def get_daily_trips(self, sheet_name: str | None, start_date: date | None,
                        end_date: date | None):

        sheet_records = self.google_sheet_reader_service.get_rows(sheet_name)

        # remove empty rows and apply filters
        rows = list(
            filter(
                lambda row: (
                        row["Fullname"] != ""
                        and (
                                not (
                                        start_date and end_date)  # start_date and end_date are falsy, so true (skip criteria)
                                or (
                                        start_date
                                        <= datetime.strptime(row["Date"], "%d/%m/%Y").date()
                                        <= end_date
                                )
                        )
                ),
                sheet_records,
            )
        )

        passenger_trips = [PassengerTrip.from_sheet_row(row) for row in rows]

        grouped_passenger_trips = defaultdict(list)

        trips = []

        # group passenger trips in a trips
        for passenger_trip in passenger_trips:
            key = (
                passenger_trip.society,
                passenger_trip.start_time,
                passenger_trip.date,
                passenger_trip.taxi,
            )

            grouped_passenger_trips[key].append(passenger_trip)

        # map the grouped passengers with Trip model
        for (society, start_time, date, taxi), passengers in grouped_passenger_trips.items():
            if not passengers:
                continue

            first_passenger = passengers[0]

            trip = Trip(society, site=first_passenger.site, start_time=start_time, date=date, taxi=taxi,
                        price=first_passenger.price, trip_passengers=passengers)
            trips.append(trip)

        # group trips by date
        trips_by_date = defaultdict(lambda: {"total_price": 0, "trips": []})

        for trip in trips:
            date_key = trip.date.strftime("%d/%m/%Y")
            trips_by_date[date_key]["date"] = trip.date.strftime("%d/%m/%Y")
            trips_by_date[date_key]["trips"].append(trip)
            trips_by_date[date_key]["total_price"] += trip.price

        trips_by_date_list = list(trips_by_date.values())

        total_price = sum(day.get("total_price", 0) for day in trips_by_date_list)
        total_trips = sum(len(day.get("trips", [])) for day in trips_by_date_list)

        # calculate total passengers with distinct by fullname
        total_passengers = sum(len(trip.trip_passengers)
                               for day in trips_by_date_list
                               for trip in day["trips"]
                               )

        return trips_by_date_list, total_trips, total_price, total_passengers
