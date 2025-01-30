from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from gmail_service import GmailService
from models import Base, Email

if __name__ == '__main__':
    engine = create_engine('sqlite:///emails.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    gmail_service = GmailService()
    gmail_service.authenticate()

    emails = gmail_service.fetch_emails()
    for email_data in emails:
        email = Email(**email_data)
        session.merge(email)
    session.commit()
