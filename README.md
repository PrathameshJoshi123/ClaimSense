# Dreamflow Backend

## Overview

Dreamflow Backend is a FastAPI-based microservices architecture designed for policy intelligence, recommendation, and simulation services. It integrates AI capabilities using LangChain, OpenAI, and Pinecone for advanced policy analysis and processing.

## Features

- **User Service**: Handles user authentication and management
- **Policy Intelligence Service**: Provides policy upload, analysis, and chat functionality
- **Policy Recommendation Service**: Offers policy recommendations
- **Shadow Claim Simulator**: Simulates claim scenarios
- **Shared Utilities**: Common authentication and utility functions

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for building AI applications
- **Pinecone**: Vector database for similarity search
- **Motor**: Asynchronous MongoDB driver
- **Pydantic**: Data validation and settings management
- **Mistral AI**: Language model for generating responses

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ClaimSense
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv myenv
   # On Windows:
   myenv\Scripts\activate
   # On macOS/Linux:
   source myenv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set up your environment variables for:

- Database connections (MongoDB)
- Mistral API key
- Pinecone API key
- Other service-specific configurations

## Running the Application

Start the FastAPI server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `/`: Root endpoint
- `/policy/*`: Policy intelligence endpoints (upload, policies, chat)
- `/shadow-claim/*`: Shadow claim simulation endpoints
- `/policy-recommendation/*`: Policy recommendation endpoints
- User service endpoints (authentication, user management)

## Development

- Use `uvicorn` for development server with auto-reload
- Run Celery workers for background tasks
- Ensure all services are properly configured and running

## Project Structure

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── services/               # Microservices
│   ├── user_service/
│   ├── policy_intelligence_service/
│   ├── policy_recommendation_service/
│   └── shadow_claim_simulator/
├── shared/                 # Shared utilities
│   └── utils/
└── temp/                   # Temporary files
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Submit pull requests for review


