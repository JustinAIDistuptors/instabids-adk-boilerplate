"""
A2A communication components for InstaBids.
This package provides tools for agent-to-agent communication
using the A2A protocol.
"""

from .client import A2AClient
from .events import (
    EventType, 
    BaseEvent,
    BidCardCreatedEvent,
    BidCardUpdatedEvent,
    ContractorInvitedEvent,
    ContractorRespondedEvent,
    MatchMadeEvent,
    MessageSentEvent
)

__all__ = [
    'A2AClient',
    'EventType',
    'BaseEvent',
    'BidCardCreatedEvent',
    'BidCardUpdatedEvent',
    'ContractorInvitedEvent',
    'ContractorRespondedEvent',
    'MatchMadeEvent',
    'MessageSentEvent'
]