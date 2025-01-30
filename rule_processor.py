from datetime import datetime, timedelta
from typing import List
from models import Email
from objects import (Ruleset, RulesetPredicate, Action, FieldName,
                     Condition, TimeUnit, DatePredicate, StringPredicate, DateConditionValue,
                     RuleAction)
import json


class RuleProcessor:
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service

    @staticmethod
    def load_rules(rules_file: str) -> Ruleset:
        with open(rules_file, 'r') as f:
            rules_data = json.load(f)
        return Ruleset(**rules_data)

    def process_email(self, email: Email, ruleset: Ruleset) -> bool:
        should_process = False

        if ruleset.predicate == RulesetPredicate.ALL:
            should_process = all(self._check_conditions(email, rule.conditions)
                                 for rule in ruleset.rules)
        else:
            should_process = any(self._check_conditions(email, rule.conditions)
                                 for rule in ruleset.rules)

        if should_process:
            for rule in ruleset.rules:
                self._apply_actions(email, rule.actions)

        return should_process

    def _check_conditions(self, email: Email, conditions: List[Condition]) -> bool:
        for condition in conditions:
            if not self._check_single_condition(email, condition):
                return False
        return True

    def _check_single_condition(self, email: Email, condition: Condition) -> bool:
        field_value = self._get_field_value(email, condition.field)

        if condition.field == FieldName.RECEIVED:
            return self._check_date_condition(
                field_value, condition.predicate, condition.value)
        else:
            return self._check_string_condition(
                field_value, condition.predicate, condition.value)

    def _get_field_value(self, email: Email, field: FieldName):
        field_map = {
            FieldName.FROM: email.from_address,
            FieldName.TO: email.to_address,
            FieldName.SUBJECT: email.subject,
            FieldName.MESSAGE: email.body,
            FieldName.RECEIVED: email.received_date
        }
        return field_map[field]

    def _check_string_condition(
            self, value: str, predicate: StringPredicate, target: str) -> bool:

        predicates = {
            StringPredicate.CONTAINS: lambda: target.lower() in value.lower(),
            StringPredicate.NOT_CONTAINS: lambda: target.lower() not in value.lower(),
            StringPredicate.EQUALS: lambda: target.lower() == value.lower(),
            StringPredicate.NOT_EQUALS: lambda: target.lower() != value.lower()
        }
        return predicates[predicate]()

    def _check_date_condition(
            self, date: str, predicate: DatePredicate,
            value: DateConditionValue) -> bool:

        if value.unit == TimeUnit.DAYS:
            delta = timedelta(days=value.value)
        else:
            delta = timedelta(days=value.value * 30)

        reference_date = datetime.now() - delta

        if predicate == DatePredicate.LESS_THAN:
            return date > reference_date
        else:  # GREATER_THAN
            return date < reference_date

    def _apply_actions(self, email: Email, actions: List[RuleAction]):
        for action in actions:
            if action.action == Action.MARK_READ:
                self._mark_as_read(email)
            elif action.action == Action.MARK_UNREAD:
                self._mark_as_unread(email)
            elif action.action == Action.MOVE_MESSAGE:
                self._move_message(email, action.parameters['destination'])

    def _mark_as_read(self, email: Email):
        self.gmail_service.service.users().messages().modify(
            userId='me',
            id=email.message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

    def _mark_as_unread(self, email:Email):
        self.gmail_service.service.users().messages().modify(
            userId='me',
            id=email.message_id,
            body={'addLabelIds': ['UNREAD']}
        )

    def _move_message(self, email: Email, destination_label: str):
        self.gmail_service.service.users().messages().modify(
            userId='me',
            id=email.message_id,
            body={
                'addLabelIds': [destination_label],
                'removeLabelIds': ['INBOX']
            }
        ).execute()