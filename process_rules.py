from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from gmail_service import GmailService
from models import Base, Email
from rule_processor import RuleProcessor

if __name__ == '__main__':
    engine = create_engine('sqlite:///emails.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    gmail_service = GmailService()
    gmail_service.authenticate()

    rule_processor = RuleProcessor(gmail_service)
    ruleset = rule_processor.load_rules('rules.json')

    for email in session.query(Email).all():
        rule_processor.process_email(email, ruleset)
