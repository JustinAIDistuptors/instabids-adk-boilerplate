"""
HomeownerAgent definition using Google ADK 1.0.0
"""
import os
from google.adk.agents import Agent
from google import genai
from google.genai import types

from .instruction import HOMEOWNER_AGENT_INSTRUCTION
from ...tools.database_tools import save_bid_card
from ...tools.vision_tools import analyze_image
from .tools.bid_card_tools import generate_bid_card

# Configure API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Define the HomeownerAgent
root_agent = Agent(
    name="HomeownerAgent",
    model="gemini-2.0-pro",  # Using Gemini 2.0 model
    description=(
        "Interactive agent that assists homeowners in scoping home improvement "
        "projects and creating structured bid cards through conversation."
    ),
    instruction=HOMEOWNER_AGENT_INSTRUCTION,
    tools=[
        analyze_image,
        generate_bid_card,
        save_bid_card,
    ],
    output_key="last_response"  # Auto-save agent's response to state
)

# Export the agent as per ADK convention
homeowner_agent = root_agent