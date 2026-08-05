from .destinations import Destination


class GoogleSheetsDestination(Destination):

    def send(self, events):

        print(f"[Google Sheets] {len(events)} eventos enviados.")

        return True
