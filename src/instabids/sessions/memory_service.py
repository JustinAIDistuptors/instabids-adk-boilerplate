"""
Custom memory implementation for ADK agents.
"""
import os
import json
from typing import Dict, Any, Optional, List
from google.adk.session import Session

from supabase import create_client, Client

from ..utils.logging import get_default_logger

logger = get_default_logger()

class InMemorySessionService:
    """
    Implements a simple in-memory session service for development purposes.
    """
    
    def __init__(self):
        """Initialize the in-memory session service."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized InMemorySessionService")
    
    def create_session(
        self, app_name: str, user_id: str, state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            state: Initial state for the session
            
        Returns:
            The created session
        """
        session = Session(
            app_name=app_name,
            user_id=user_id,
            state=state or {}
        )
        
        # Store session in memory
        self.sessions[session.id] = {
            "app_name": app_name,
            "user_id": user_id,
            "state": session.state.copy(),
            "events": []
        }
        
        logger.info(f"Created session: {session.id} for user: {user_id}")
        return session
    
    def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        """
        Get an existing session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            The session if found, None otherwise
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        session_data = self.sessions[session_id]
        
        # Verify app_name and user_id
        if session_data["app_name"] != app_name or session_data["user_id"] != user_id:
            logger.warning(
                f"Session {session_id} does not match app_name={app_name} "
                f"and user_id={user_id}"
            )
            return None
        
        # Create session from stored data
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=session_data["state"].copy()
        )
        
        return session
    
    def list_sessions(self, app_name: str, user_id: str) -> List[str]:
        """
        List all sessions for a user.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        session_ids = []
        
        for session_id, session_data in self.sessions.items():
            if session_data["app_name"] == app_name and session_data["user_id"] == user_id:
                session_ids.append(session_id)
        
        return session_ids
    
    def delete_session(self, app_name: str, user_id: str, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if the session was deleted, False otherwise
        """
        if session_id not in self.sessions:
            logger.warning(f"Cannot delete session {session_id}: not found")
            return False
        
        session_data = self.sessions[session_id]
        
        # Verify app_name and user_id
        if session_data["app_name"] != app_name or session_data["user_id"] != user_id:
            logger.warning(
                f"Cannot delete session {session_id}: does not match "
                f"app_name={app_name} and user_id={user_id}"
            )
            return False
        
        # Delete session
        del self.sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        
        return True
    
    def append_event(self, session: Session, event: Any) -> None:
        """
        Append an event to a session.
        
        Args:
            session: The session to append the event to
            event: The event to append
        """
        if session.id not in self.sessions:
            logger.warning(f"Cannot append event to session {session.id}: not found")
            return
        
        # Append event
        self.sessions[session.id]["events"].append(event)
        
        # Update session state if event has state_delta
        if hasattr(event, "actions") and hasattr(event.actions, "state_delta"):
            for key, value in event.actions.state_delta.items():
                # Update state in memory
                self.sessions[session.id]["state"][key] = value
                # Update state in session object
                session.state[key] = value
        
        logger.debug(f"Appended event to session: {session.id}")
    
    def list_events(self, app_name: str, user_id: str, session_id: str) -> List[Any]:
        """
        List all events for a session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of events
        """
        if session_id not in self.sessions:
            logger.warning(f"Cannot list events for session {session_id}: not found")
            return []
        
        session_data = self.sessions[session_id]
        
        # Verify app_name and user_id
        if session_data["app_name"] != app_name or session_data["user_id"] != user_id:
            logger.warning(
                f"Cannot list events for session {session_id}: does not match "
                f"app_name={app_name} and user_id={user_id}"
            )
            return []
        
        return session_data["events"]


class SupabaseMemoryService:
    """
    Implements a Supabase-backed session service for production use.
    """
    
    def __init__(self):
        """Initialize the Supabase session service."""
        # Get Supabase credentials from environment
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        # Initialize Supabase client
        self.supabase = create_client(url, key)
        logger.info("Initialized SupabaseMemoryService")
        
        # Ensure tables exist
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self) -> None:
        """Ensure that required tables exist in the database."""
        # Note: In a real implementation, you would use proper migrations
        # This is a simplified example
        
        # Check if the sessions table exists
        try:
            # Just query the table to see if it exists
            self.supabase.table("instabids.agent_sessions").select("id").limit(1).execute()
        except Exception as e:
            logger.warning(f"Sessions table does not exist or is not accessible: {e}")
            # In a real implementation, you would create the table
            # For this example, we'll just log a warning
    
    def create_session(
        self, app_name: str, user_id: str, state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            state: Initial state for the session
            
        Returns:
            The created session
        """
        session = Session(
            app_name=app_name,
            user_id=user_id,
            state=state or {}
        )
        
        # Store session in Supabase
        self.supabase.table("instabids.agent_sessions").insert({
            "id": session.id,
            "app_name": app_name,
            "user_id": user_id,
            "state": json.dumps(session.state)
        }).execute()
        
        logger.info(f"Created session: {session.id} for user: {user_id}")
        return session
    
    def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        """
        Get an existing session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            The session if found, None otherwise
        """
        result = self.supabase.table("instabids.agent_sessions").select("*").eq("id", session_id).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        session_data = result.data[0]
        
        # Verify app_name and user_id
        if session_data["app_name"] != app_name or session_data["user_id"] != user_id:
            logger.warning(
                f"Session {session_id} does not match app_name={app_name} "
                f"and user_id={user_id}"
            )
            return None
        
        # Parse state from JSON
        state = json.loads(session_data["state"]) if session_data["state"] else {}
        
        # Create session from stored data
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state
        )
        
        return session
    
    def list_sessions(self, app_name: str, user_id: str) -> List[str]:
        """
        List all sessions for a user.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        result = self.supabase.table("instabids.agent_sessions") \
            .select("id") \
            .eq("app_name", app_name) \
            .eq("user_id", user_id) \
            .execute()
        
        if not result.data:
            return []
        
        session_ids = [item["id"] for item in result.data]
        return session_ids
    
    def delete_session(self, app_name: str, user_id: str, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if the session was deleted, False otherwise
        """
        # First, check if the session exists and belongs to the user/app
        result = self.supabase.table("instabids.agent_sessions") \
            .select("id") \
            .eq("id", session_id) \
            .eq("app_name", app_name) \
            .eq("user_id", user_id) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(
                f"Cannot delete session {session_id}: not found or does not match "
                f"app_name={app_name} and user_id={user_id}"
            )
            return False
        
        # Delete session
        self.supabase.table("instabids.agent_sessions").delete().eq("id", session_id).execute()
        
        # Delete related events
        self.supabase.table("instabids.agent_events").delete().eq("session_id", session_id).execute()
        
        logger.info(f"Deleted session: {session_id}")
        return True
    
    def append_event(self, session: Session, event: Any) -> None:
        """
        Append an event to a session.
        
        Args:
            session: The session to append the event to
            event: The event to append
        """
        # Store event in Supabase
        event_data = {
            "session_id": session.id,
            "invocation_id": getattr(event, "invocation_id", None),
            "author": getattr(event, "author", None),
            "timestamp": getattr(event, "timestamp", None),
            "event_data": json.dumps({
                "content": getattr(event, "content", None),
                "actions": getattr(event, "actions", None)
            })
        }
        
        self.supabase.table("instabids.agent_events").insert(event_data).execute()
        
        # Update session state if event has state_delta
        if hasattr(event, "actions") and hasattr(event.actions, "state_delta"):
            # Get current state
            result = self.supabase.table("instabids.agent_sessions") \
                .select("state") \
                .eq("id", session.id) \
                .execute()
            
            if result.data and len(result.data) > 0:
                current_state = json.loads(result.data[0]["state"]) if result.data[0]["state"] else {}
                
                # Update state with delta
                for key, value in event.actions.state_delta.items():
                    current_state[key] = value
                    # Update state in session object as well
                    session.state[key] = value
                
                # Save updated state
                self.supabase.table("instabids.agent_sessions") \
                    .update({"state": json.dumps(current_state)}) \
                    .eq("id", session.id) \
                    .execute()
        
        logger.debug(f"Appended event to session: {session.id}")
    
    def list_events(self, app_name: str, user_id: str, session_id: str) -> List[Any]:
        """
        List all events for a session.
        
        Args:
            app_name: Name of the application
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of events
        """
        # First, check if the session exists and belongs to the user/app
        session_result = self.supabase.table("instabids.agent_sessions") \
            .select("id") \
            .eq("id", session_id) \
            .eq("app_name", app_name) \
            .eq("user_id", user_id) \
            .execute()
        
        if not session_result.data or len(session_result.data) == 0:
            logger.warning(
                f"Cannot list events for session {session_id}: not found or does not match "
                f"app_name={app_name} and user_id={user_id}"
            )
            return []
        
        # Get events
        events_result = self.supabase.table("instabids.agent_events") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("timestamp", {"ascending": True}) \
            .execute()
        
        if not events_result.data:
            return []
        
        # Convert DB rows to event objects
        # In a real implementation, you would convert to proper Event objects
        # This is a simplified example
        events = []
        for event_data in events_result.data:
            # Parse event_data JSON
            event_json = json.loads(event_data["event_data"])
            
            # Create a simple dict for demonstration
            # In a real implementation, you would create Event objects
            event = {
                "invocation_id": event_data["invocation_id"],
                "author": event_data["author"],
                "timestamp": event_data["timestamp"],
                "content": event_json.get("content"),
                "actions": event_json.get("actions")
            }
            
            events.append(event)
        
        return events