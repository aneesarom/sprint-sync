# SprintSync Backend API

SprintSync is a powerful backend API designed to streamline sprint project estimation and strategy. It offers robust user and task management, complemented by advanced AI capabilities for intelligent suggestions and resume processing. This application leverages modern technologies to provide a seamless and efficient experience for managing development sprints.

## Features

*   **User Management**: Secure user registration, login, and profile management with JWT authentication. Supports admin roles for privileged operations.
*   **Task Management**: Comprehensive task creation, assignment, tracking, and status updates (`created`, `assigned`, `in_process`, `completed`).
*   **AI-Powered Suggestions**:
    *   **Task Description Generation**: Generate detailed and relevant task descriptions using advanced AI models (Google Gemini and Groq).
    *   **Intelligent Search**: Hybrid search (keyword and vector-based) for profiles/resumes, enhancing the ability to find suitable candidates or resources.
*   **Resume Processing**: Upload PDF resumes, extract key skills and tasks using AI, and store relevant information for efficient retrieval and analysis.
*   **Scalable Backend**: Built with FastAPI for high performance and scalability.
*   **Data Storage**: Utilizes Supabase for database management and S3-compatible storage for resume files.
*   **Observability**: Integrated Prometheus instrumentation for monitoring API performance.

## Technologies Used

*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+.
*   **Supabase**: An open-source Firebase alternative providing a PostgreSQL database, vector search support, and more.
*   **LangChain**: Framework for developing GEN AI applications powered by language models.
*   **Google Gemini**: Advanced generative AI models for natural language understanding and generation.
*   **Groq**: High-performance inference engine for AI models.
*   **Tavily API**: For intelligent web search capabilities, enhancing AI agent responses.
*   **Amazon S3 (or S3-compatible storage)**: For storing uploaded resume files.
*   **Uvicorn**: ASGI server for running FastAPI applications.
*   **Python-Jose & Passlib**: For secure JWT handling and password hashing.
*   **Pydantic**: Data validation and settings management using Python type hints.
*   **Prometheus FastAPI Instrumentator**: For collecting metrics from the FastAPI application.
*   **Dotenv**: For managing environment variables.
*   **PyPDF**: For extracting text from PDF documents.

## Setup and Installation

### Prerequisites

*   Python 3.11
*   Docker (optional, for containerized deployment)
*   Supabase project with appropriate tables (`users`, `tasks`, `resumes`) and `vector_search_profile`, `keyword_search_profile` RPC functions.
*   AWS S3 bucket (or compatible) configured for resume storage.
*   Google Gemini API Key, Groq API Key, and Tavily API Key.

### Environment Variables

Rename `.env.example` to  `.env` and add values

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/sprint-sync.git
    cd sprint-sync
    ```
2.  **Initialize Poetry and install dependencies:**
    ```bash
    poetry install
    ```
    This command reads the `pyproject.toml` file and installs all the declared dependencies, creating a virtual environment

### Running the Application

To run the application locally:

```bash
poetry run uvicorn app.main:app  --reload --port 8000
```

The API documentation will be available at `http://127.0.0.1:8000/docs`.

### Local Docker Deployment

To build and run the Docker image:

```bash
docker build -t sprint-sync .
docker run -p 8000:8000 sprint-sync
```

### Render Deployment

This project is deployed on `Render`

## API Endpoints

The API exposes the following main routes:

*   `/users`: User authentication and management.
*   `/tasks`: Task creation, retrieval, updates, and deletion.
*   `/ai`: AI-powered task description suggestions and profile analysis.
*   `/resumes`: Resume upload and processing.
*   `/metrics`: Prometheus metrics endpoint for monitoring.


Refer to the interactive API documentation (`/docs`) for detailed information on all available endpoints and their request/response schemas.

## Supabase Migrations

The `app/supabase/migrations` directory contains SQL migration files for setting up your Supabase database. These include:

*   `initial_schema.sql`: Sets up the initial `users`, `tasks`, and `resumes` tables.
*   `vector_search.sql`: Defines the `vector_search_profile` function for semantic search.
*   `keyword_search.sql`: Defines the `keyword_search_profile` function for keyword search.
*   `get_userid_ordered.sql`: A utility function to retrieve user IDs in a specific order.

You should apply these migrations to your Supabase project to ensure the database is correctly configured.

## Loom Video Link
https://drive.google.com/drive/folders/1mLmi9gqqG-r2RBjC_BlVf-fk5v33Pm2m?usp=sharing

