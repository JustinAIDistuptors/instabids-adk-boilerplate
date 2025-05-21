"""
A2A client for communicating with other agents.
"""
from typing import Dict, Any, Optional, AsyncGenerator
import json
import uuid
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class A2AClient:
    """Client for interacting with A2A-enabled agents."""
    
    def __init__(self, agent_url: str, auth_token: Optional[str] = None):
        """
        Initialize the A2A client.
        
        Args:
            agent_url: The base URL of the A2A-enabled agent.
            auth_token: Optional authentication token.
        """
        self.agent_url = agent_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
    
    async def send_task(self, message: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a task to an A2A agent (tasks/send method).
        
        Args:
            message: The message to send to the agent.
            task_id: Optional task ID, generated if not provided.
            
        Returns:
            The response from the agent.
        """
        task_id = task_id or str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": session_id,
                "message": message
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agent_url}",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during A2A task send: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during A2A task send: {str(e)}")
            raise
    
    async def send_task_subscribe(
        self, message: Dict[str, Any], task_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a task and subscribe to streaming updates (tasks/sendSubscribe method).
        
        Args:
            message: The message to send to the agent.
            task_id: Optional task ID, generated if not provided.
            
        Yields:
            Updates from the agent as they arrive.
        """
        task_id = task_id or str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/sendSubscribe",
            "params": {
                "id": task_id,
                "sessionId": session_id,
                "message": message
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.agent_url}",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    
                    # Process SSE events
                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        if buffer.endswith("\n\n"):
                            events = buffer.split("\n\n")
                            buffer = ""
                            
                            for event in events:
                                if event.strip():
                                    # Parse the SSE event
                                    event_data = None
                                    for line in event.split("\n"):
                                        if line.startswith("data: "):
                                            event_data = line[6:]
                                            break
                                    
                                    if event_data:
                                        try:
                                            yield json.loads(event_data)
                                        except json.JSONDecodeError:
                                            logger.error(f"Failed to parse SSE event data: {event_data}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during A2A streaming: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during A2A streaming: {str(e)}")
            raise