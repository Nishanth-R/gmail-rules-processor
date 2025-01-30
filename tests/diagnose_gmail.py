import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests


class GmailConnectionTest:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def test_internet_connection(self):
        try:
            self.logger.info("Testing internet connection to Google...")
            response = requests.get('https://www.google.com', timeout=5)
            self.logger.info(f"Google connection successful: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Internet connection test failed: {str(e)}")
            return False

    def test_connection(self):
        try:
            if not self.test_internet_connection():
                raise ConnectionError("Cannot connect to Google. Please check your internet connection.")

            creds = None
            if os.path.exists('../token.pickle'):
                with open('../token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    self.logger.info("Getting new credentials...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        '../token.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)

                with open('../token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            # Build service with only credentials
            self.logger.info("Building Gmail service...")
            service = build('gmail', 'v1', credentials=creds)

            self.logger.info("Testing Gmail API connection...")
            try:
                profile = service.users().labels().list(userId='me').execute()
                self.logger.info(f"Successfully connected as: {profile['emailAddress']}")

                labels = service.users().labels().list(userId='me').execute()
                self.logger.info(f"Successfully retrieved {len(labels['labels'])} labels")

                self.logger.info("Attempting to list messages...")
                messages = service.users().messages().list(
                    userId='me',
                    maxResults=1
                ).execute()
                self.logger.info("Successfully listed messages")

                return {
                    'email': profile['emailAddress'],
                    'label_count': len(labels['labels']),
                    'has_messages': bool(messages.get('messages', []))
                }

            except HttpError as error:
                self.logger.error(f"Gmail API Error: {str(error)}")
                if error.resp.status == 403:
                    self.logger.error("Permission denied. Please check API scopes.")
                elif error.resp.status == 429:
                    self.logger.error("Too many requests. Please try again later.")
                raise

        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            raise


def main():
    print("\nStarting Gmail API Connection Test...")
    print("=====================================")

    if os.path.exists('../token.pickle'):
        os.remove('../token.pickle')
        print("Removed existing credentials for fresh test.")

    tester = GmailConnectionTest()

    try:
        results = tester.test_connection()
        print("\nConnection Test Results:")
        print("=======================")
        print(f" Connected to Gmail account: {results['email']}")
        print(f" Found {results['label_count']} labels")
        print(f" Successfully tested message listing")
        print("\nAll connection tests passed successfully!")
    except Exception as e:
        print(f"\n Connection test failed: {str(e)}")


if __name__ == "__main__":
    main()