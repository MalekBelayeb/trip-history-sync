from google.oauth2.service_account import Credentials
import gspread
from config import Config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GoogleSheetReaderService:
    def __init__(self):
        credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        self.client = gspread.authorize(credentials)

    def get_rows(self, worksheet):
        sheet = self.client.open_by_key(Config.GOOGLE_SHEET_ID).worksheet(worksheet)

        return sheet.get_all_records()
