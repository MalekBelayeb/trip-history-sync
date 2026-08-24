import time
from .google_sheet_reader_service import GoogleSheetReaderService
from app.models import PassengerTrip, Trip
from collections import defaultdict


class ExcelSynchronizerService:
    def __init__(self, google_sheet_reader_service: GoogleSheetReaderService):
        self.google_sheet_reader_service = google_sheet_reader_service

    def get_trips_from_sheet(self, sheet_name: str):
        sheet_records = self.google_sheet_reader_service.get_rows(str(sheet_name))

        # remove empty rows and apply filters
        rows = list(
            filter(
                lambda row: (
                        row["Fullname"] != ""
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

            trip = Trip(
                id=f"{society}_{start_time}_{date}_{taxi}", society=society, site=first_passenger.site,
                start_time=start_time,
                date=date, taxi=str(taxi),
                price=first_passenger.price, trip_passengers=passengers)
            trips.append(trip)

        return trips, sheet_records

    def get_trips_from_driver_sheets(self, drivers):
        driver_ranges = [
            f"'{driver}'!A:J"
            for driver in drivers
        ]

        response = self.google_sheet_reader_service.get_rows_batch(driver_ranges)

        driver_trips = {}

        for value_range in response["valueRanges"]:
            range_name = value_range["range"]

            # "'22290348'!A1:J100" -> "22290348"
            driver = range_name.split("'")[1]

            values = value_range.get("values", [])

            if not values:
                driver_trips[driver] = ([], [])
                continue

            # First row contains headers
            headers = values[0]

            # Convert rows to the same format returned by get_all_records()
            sheet_records = [
                dict(zip(headers, row))
                for row in values[1:]
            ]

            # Same logic as your existing get_trips_from_sheet()
            rows = list(
                filter(
                    lambda row: row.get("Fullname", "") != "",
                    sheet_records,
                )
            )

            passenger_trips = [
                PassengerTrip.from_sheet_row(row)
                for row in rows
            ]

            grouped_passenger_trips = defaultdict(list)

            for passenger_trip in passenger_trips:
                key = (
                    passenger_trip.society,
                    passenger_trip.start_time,
                    passenger_trip.date,
                    passenger_trip.taxi,
                )

                grouped_passenger_trips[key].append(passenger_trip)

            trips = []

            for (
                    society,
                    start_time,
                    date,
                    taxi
            ), passengers in grouped_passenger_trips.items():

                if not passengers:
                    continue

                first_passenger = passengers[0]

                trip = Trip(
                    id=f"{society}_{start_time}_{date}_{taxi}",
                    society=society,
                    site=first_passenger.site,
                    start_time=start_time,
                    date=date,
                    taxi=str(taxi),
                    price=first_passenger.price,
                    trip_passengers=passengers,
                )

                trips.append(trip)

            driver_trips[driver] = (
                trips,
                sheet_records
            )

        return driver_trips

    def synchronize_driver_trips(self, company_trips: list[Trip], driver_trips, driver: str):

        driver_phone_number = str(driver)

        if driver_trips is not None:
            driver_trips, driver_sheet_records = driver_trips
        else:
            driver_trips, driver_sheet_records = self.get_trips_from_sheet(str(driver_phone_number))

        filtered_driver_trips_from_company = [
            trip
            for trip in company_trips
            if str(trip.taxi) == str(driver_phone_number)
        ]

        driver_trip_ids = {trip.id for trip in driver_trips}

        new_trips_driver = [
            trip
            for trip in filtered_driver_trips_from_company
            if trip.id not in driver_trip_ids
        ]

        next_row_index = len(driver_sheet_records) + 2  # header row + next row
        rows_to_append = []

        for new_trip in new_trips_driver:
            rows_to_append.append({})

            for index, passenger in enumerate(new_trip.trip_passengers):
                rows_to_append.append({"Fullname": passenger.passenger,
                                       "Pickup": passenger.pickup,
                                       "Dropoff": passenger.dropoff,
                                       "Phone Number": passenger.phone,
                                       "Start Time": new_trip.start_time,
                                       "Society": new_trip.society, "Site": new_trip.site,
                                       "Price": new_trip.price, "Taxi": new_trip.taxi,
                                       "Date": new_trip.date.strftime("%d/%m/%Y"), },
                                      )

        self.google_sheet_reader_service.append_rows(str(driver_phone_number), rows_to_append, next_row_index)

        return len(new_trips_driver)

    def synchronize_trips_by_company_and_driver(self, company: str, driver: str):
        company_trips, company_sheet_records = self.get_trips_from_sheet(str(company))

        trip_count = self.synchronize_driver_trips(company_trips, None, driver)

        return trip_count

    def synchronize_trips_by_company(self, company: str):
        company_trips, _ = self.get_trips_from_sheet(str(company))
        drivers = {trip.taxi for trip in company_trips if trip.taxi}
        print(drivers)

        drivers_trips = self.get_trips_from_driver_sheets(drivers)

        results = {}

        for driver in drivers:
            print("--------------------")
            print("Driver: {} ".format(driver))

            for attempt in range(6, 10):
                print("Attempt: {} ".format(attempt))

                try:
                    trip_count = self.synchronize_driver_trips(
                        company_trips,
                        drivers_trips[str(driver)],
                        driver
                    )
                    print("Trip count: {} ".format(trip_count))
                    results[driver] = trip_count
                    break

                except Exception as e:
                    print(e)
                    if "429" not in str(e):
                        raise

                    wait_time = 2 ** attempt  # Exponential backoff
                    print("Waiting {} seconds...".format(wait_time))
                    time.sleep(wait_time)

        return results
