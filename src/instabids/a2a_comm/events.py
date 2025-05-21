"""
A2A event definitions for InstaBids.
"""
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Types of events that can be exchanged between agents."""
    BID_CARD_CREATED = "bid_card_created"
    BID_CARD_UPDATED = "bid_card_updated"
    CONTRACTOR_INVITED = "contractor_invited"
    CONTRACTOR_RESPONDED = "contractor_responded"
    MATCH_MADE = "match_made"
    MESSAGE_SENT = "message_sent"

class BaseEvent(BaseModel):
    """Base event model with common fields."""
    event_type: EventType
    timestamp: str = Field(...)  # ISO format timestamp
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    
class BidCardCreatedEvent(BaseEvent):
    """Event fired when a new bid card is created."""
    event_type: EventType = EventType.BID_CARD_CREATED
    bid_card_id: str
    homeowner_id: str
    project_type: str
    bid_card_data: Dict[str, Any]

class BidCardUpdatedEvent(BaseEvent):
    """Event fired when a bid card is updated."""
    event_type: EventType = EventType.BID_CARD_UPDATED
    bid_card_id: str
    updated_fields: List[str]
    bid_card_data: Dict[str, Any]

class ContractorInvitedEvent(BaseEvent):
    """Event fired when a contractor is invited to bid."""
    event_type: EventType = EventType.CONTRACTOR_INVITED
    bid_card_id: str
    contractor_id: str
    invitation_method: str  # "email", "sms", etc.

class ContractorRespondedEvent(BaseEvent):
    """Event fired when a contractor responds to an invitation."""
    event_type: EventType = EventType.CONTRACTOR_RESPONDED
    bid_card_id: str
    contractor_id: str
    response: str  # "interested", "not_interested", "needs_more_info"
    message: Optional[str] = None

class MatchMadeEvent(BaseEvent):
    """Event fired when a homeowner-contractor match is made."""
    event_type: EventType = EventType.MATCH_MADE
    bid_card_id: str
    homeowner_id: str
    contractor_id: str
    match_timestamp: str

class MessageSentEvent(BaseEvent):
    """Event fired when a message is sent in a conversation."""
    event_type: EventType = EventType.MESSAGE_SENT
    conversation_id: str
    sender_id: str
    sender_type: str  # "homeowner", "contractor", "system"
    message_id: str
    content: str
    attachments: Optional[List[Dict[str, str]]] = None