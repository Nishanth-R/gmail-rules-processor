from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from gmail_service import GmailService
from models import Base, Email
from rule_processor import RuleProcessor

def main():
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

    rule_processor = RuleProcessor(gmail_service)
    ruleset = rule_processor.load_rules('rules.json')

    for email in session.query(Email).all():
        rule_processor.process_email(email, ruleset)


if __name__ == "__main__":
    main()