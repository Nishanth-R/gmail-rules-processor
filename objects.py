from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel

class FieldName(str, Enum):
    FROM = "from"
    TO = "to"
    SUBJECT = "subject"
    MESSAGE = "message"
    RECEIVED = "received"

class StringPredicate(str, Enum):
    CONTAINS = "contains"
    NOT_CONTAINS = "does_not_contain"
    EQUALS = "equals"
    NOT_EQUALS = "does_not_equal"

class DatePredicate(str, Enum):
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"

class TimeUnit(str, Enum):
    DAYS = "days"
    MONTHS = "months"

class Action(str, Enum):
    MARK_READ = "mark_as_read"
    MARK_UNREAD = "mark_as_unread"
    MOVE_MESSAGE = "move_message"

class RulesetPredicate(str, Enum):
    ALL = "all"
    ANY = "any"

class DateConditionValue(BaseModel):
    value: int
    unit: TimeUnit

class Condition(BaseModel):
    field: FieldName
    predicate: Union[StringPredicate, DatePredicate]
    value: Union[str, DateConditionValue]

class RuleAction(BaseModel):
    action: Action
    parameters: Optional[dict] = None

class Rule(BaseModel):
    name: str
    conditions: List[Condition]
    actions: List[RuleAction]

class Ruleset(BaseModel):
    name: str
    predicate: RulesetPredicate
    rules: List[Rule]