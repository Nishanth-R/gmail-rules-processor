from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import os
import logging
from base64 import urlsafe_b64decode


class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, credentials_path='token.json'):
        self.credentials_path = credentials_path
        self.creds = None
        self.service = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def authenticate(self):
        """Handles the Gmail API authentication process.
        :return:
        True - In case of authentication success
        FileNotFoundError - In case of Input file not being found
        HttpError - In case of
        """
        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
                    self.logger.info("Loaded existing credentials from token.pickle")

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.logger.info("Refreshing expired credentials")
                    self.creds.refresh(Request())
                else:
                    self.logger.info("Initiating new OAuth2 flow")
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            f"Credentials file not found at {self.credentials_path}. "
                            "Please download it from Google Cloud Console."
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.SCOPES,
                        redirect_uri='http://localhost:8080'  # Specify a fixed port
                    )

                    self.creds = flow.run_local_server(
                        port=8080,
                        access_type='offline',
                        include_granted_scopes='true'
                    )

                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
                    self.logger.info("Saved new credentials to token.pickle")

            self.service = build('gmail', 'v1', credentials=self.creds)
            self.logger.info("Successfully authenticated with Gmail API")

            return True

        except FileNotFoundError as e:
            self.logger.error(f"Authentication failed as token.json not found : {str(e)}")
            raise
        except HttpError as error:
            self.logger.error(f"Gmail API Error: {str(error)}")
            if error.resp.status == 403:
                self.logger.error("Permission denied. Please check API scopes.")
            elif error.resp.status == 429:
                self.logger.error("Too many requests. Please try again later.")
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    def fetch_emails(self, max_results=100):
        results = self.service.users().messages().list(
            userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = self.service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()

            headers = msg['payload']['headers']
            email_data = {
                'message_id': msg['id'],
                'thread_id': msg['threadId'],
                'from_address': next(h['value'] for h in headers if h['name'].lower() == 'from'),
                'to_address': next(h['value'] for h in headers if h['name'].lower() == 'to'),
                'subject': next(h['value'] for h in headers if h['name'].lower() == 'subject'),
                'received_date': next(h['value'] for h in headers if h['name'].lower() == 'date'),
                'body': self._get_body(msg),
                'is_read': 'UNREAD' not in msg['labelIds'],
                'label_ids': ','.join(msg['labelIds'])
            }
            emails.append(email_data)

        return emails

    def _get_body(self, message):
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    return urlsafe_b64decode(
                        part['body']['data']).decode('utf-8')
        elif 'body' in message['payload']:
            return urlsafe_b64decode(
                message['payload']['body']['data']).decode('utf-8')
        return ""
