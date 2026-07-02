from .google_sheet_reader_service import GoogleSheetReaderService
from .trip_history_service import TripHistoryService
from datetime import date, datetime
from app.utils import convert_amount_to_words


class InvoiceCalculationService:
    def __init__(self, google_sheet_reader_service: GoogleSheetReaderService, trip_history_service: TripHistoryService):
        self.google_sheet_reader_service = google_sheet_reader_service
        self.trip_history_service = trip_history_service

    def get_invoice_results(self, company, date_from, date_to):
        trips_by_date_list, total_trips, total_price, total_passengers = self.trip_history_service.get_daily_trips(
            company,
            date_from,
            date_to,
        )

        sheet_records = self.google_sheet_reader_service.get_rows("Companies")

        company_row = list(
            filter(
                lambda row: (
                        row.get("Company", "") == company
                ),
                sheet_records,
            )
        )

        today = date.today()
        year = datetime.now().year

        profit_margin = company_row[0].get("Profit Margin", "") if len(company_row) > 0 else 0
        address = company_row[0].get("Address", "") if len(company_row) > 0 else ""
        mf = company_row[0].get("Matricule Fiscal", "") if len(company_row) > 0 else ""

        service_fee = (total_price * profit_margin) / 100

        service_fee_tva = (service_fee * 19) / 100

        final_price_without_tva = total_price + service_fee

        final_price_with_tva = total_price + service_fee + service_fee_tva

        final_price_with_tva_words = convert_amount_to_words(final_price_with_tva)

        fiscal_stamp = 1.0

        return today, year, company, address, mf, date_from, date_to, total_trips, total_price, service_fee, service_fee_tva, fiscal_stamp, profit_margin, final_price_with_tva, final_price_with_tva_words, final_price_without_tva
