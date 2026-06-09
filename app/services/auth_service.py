from app.models import Account
from .google_sheet_reader_service import GoogleSheetReaderService


class AuthService:
    def __init__(self, google_sheet_reader_service: GoogleSheetReaderService):
        self.google_sheet_reader_service = google_sheet_reader_service

    def login(self, email, password):
        sheet_records = self.google_sheet_reader_service.get_rows("Companies")
        rows = list(
            filter(
                lambda row: (
                        row.get("Login", "") == email
                        and str(row.get("Password", "")).strip() == str(password).strip()
                ),
                sheet_records,
            )
        )

        if len(rows) != 0:
            account = Account(rows[0].get("Login", "").strip(), "", rows[0].get("Company", ""), "COMPANY", "")
            return account

        sheet_records = self.google_sheet_reader_service.get_rows("Drivers")

        rows = list(
            filter(
                lambda row: (
                        str(row.get("Login", "")) == email
                        and str(row.get("Password", "")).strip() == str(password).strip()
                ),
                sheet_records,
            )
        )

        if len(rows) != 0:
            account = Account(rows[0].get("Login", ""), "", rows[0].get("Fullname", ""), "DRIVER",
                              rows[0].get("Immat", ""))
            return account

        return None
