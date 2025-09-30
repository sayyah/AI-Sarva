from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import json

# Define possible trading actions as an enumeration


class Action(Enum):
    BUY = auto()
    SELL = auto()
    HOLD = auto()
    SHORT = auto()
    LONG = auto()


@dataclass(frozen=True)
class NewsArticle:
    """Structured news data"""
    url: str
    title: str
    content: str
    published_date: Optional[str] = None
    source: Optional[str] = None

    def to_json(self):
        # Serializes the object to JSON format
        return json.dumps(dataclass.asdict(self))


@dataclass(frozen=True)
class TradingDecision:
    """Structured trading decision"""
    coin: str
    action: Action  # Use Action enum for type safety and clearer semantics
    amount: float
    confidence: float
    reasoning: Optional[str] = None

    def to_json(self):
        # Serializes the object to JSON format, converting Enum values to strings
        return json.dumps({"action": self.action.name, **dataclass.asdict(self)})
