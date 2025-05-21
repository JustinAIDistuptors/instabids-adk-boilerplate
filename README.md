# InstaBids: ADK 1.0.0 & A2A Boilerplate

A comprehensive boilerplate for building multi-agent systems using Google Agent Development Kit (ADK) 1.0.0 and Agent-to-Agent (A2A) protocol. This project provides a solid foundation for creating an "agentic business army" - a scalable multi-agent system for connecting homeowners with contractors through AI-assisted project scoping and bidding.

## Features

- **ADK 1.0.0 Integration**: Built with the latest Google ADK release (May 2025)
- **A2A Protocol Support**: Full implementation of Agent-to-Agent communication
- **Multi-Agent Architecture**: Modular agent design with specialized responsibilities
- **Session Management**: Robust state handling with user, session, and app-level persistence
- **FastAPI Backend**: Modern Python API with async support
- **Supabase Integration**: Database and authentication infrastructure
- **Comprehensive Testing**: Unit and integration test frameworks

## Getting Started

### Prerequisites

- Python 3.10+
- Poetry (recommended) or pip
- Google API Key for Gemini models
- Supabase account (for database functionality)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/instabids-adk-boilerplate.git
   cd instabids-adk-boilerplate
   ```

2. Set up your environment:
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # OR using pip
   pip install -r requirements.txt
   ```

3. Create your environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Running the Application

To start the agent development UI:
```bash
# Make sure to run from the parent directory of your agent package
cd instabids-adk-boilerplate
adk web
```

Open your browser at http://localhost:8000

## Project Structure

```
instabids/
├── .a2a/                         # A2A-specific configurations
│   ├── agent_cards/              # JSON definitions of agent capabilities
│   └── schemas/                  # Shared message/event schemas for A2A
├── .adk/                         # ADK-specific configurations
│   ├── context.json              # Project-wide context for AI consumption
│   ├── conventions.json          # Coding standards/patterns
│   └── components.json           # Component registry for agents
├── src/
│   └── instabids/
│       ├── a2a_comm/             # A2A communication components
│       ├── agents/               # Agent implementations
│       ├── api/                  # FastAPI application
│       ├── modules/              # Shared business logic modules
│       ├── sessions/             # ADK session management
│       ├── tools/                # Shared tools for agents
│       └── utils/                # Common utility functions
└── tests/                        # Test directory
```

## Documentation

For more detailed information, see:
- [ADK_README.md](ADK_README.md) - ADK framework specific instructions
- [A2A_README.md](A2A_README.md) - A2A protocol specific instructions
- [AI_README.md](AI_README.md) - Overall AI agent instructions

## License

This project is licensed under the MIT License - see the LICENSE file for details.