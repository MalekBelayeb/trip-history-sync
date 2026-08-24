from google.oauth2.service_account import Credentials
import gspread
from gspread.utils import ValueInputOption
from gspread_formatting import format_cell_range, CellFormat, Color

from config import Config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

HEADERS = [
    "Fullname",
    "Pickup",
    "Dropoff",
    "Phone Number",
    "Start Time",
    "Society",
    "Site",
    "Price",
    "Taxi",
    "Date",
]


class GoogleSheetReaderService:
    def __init__(self):
        credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(
            Config.GOOGLE_SHEET_ID
        )

    def get_rows(self, worksheet):
        sheet = self.spreadsheet.worksheet(worksheet)

        return sheet.get_all_records()

    def get_rows_batch(self, data_ranges):
        return self.spreadsheet.values_batch_get(
            data_ranges
        )

    def append_row(self, worksheet, row, next_row_index, is_separator):
        sheet = self.spreadsheet.worksheet(worksheet)
        if is_separator == True:
            sheet.format(
                f"A{next_row_index}:J{next_row_index}",
                {
                    "backgroundColor": {
                        "red": 229,
                        "green": 229,
                        "blue": 229
                    }
                })

        sheet.update(range_name=f"A{next_row_index}:J{next_row_index}", values=[row],
                     value_input_option=ValueInputOption.user_entered)

    def append_rows(self, worksheet, rows, next_row_index):
        sheet = self.spreadsheet.worksheet(worksheet)

        values = [
            [row.get(header, "") for header in HEADERS]
            for row in rows
        ]

        sheet.update(range_name=f"A{next_row_index}:J{next_row_index + len(values)}",
                     values=values,
                     value_input_option=ValueInputOption.user_entered)

        # 2. Find separator rows
        separator_rows = [
            next_row_index + index
            for index, row in enumerate(rows)
            if not row
        ]

        if not separator_rows:
            return

        # 3. Format all separators in one batch
        requests = []

        for row_number in separator_rows:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": row_number - 1,
                        "endRowIndex": row_number,
                        "startColumnIndex": 0,
                        "endColumnIndex": 10,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.9,
                                "green": 0.9,
                                "blue": 0.9,
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            })

        sheet.spreadsheet.batch_update({
            "requests": requests
        })
