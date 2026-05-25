# AI Support Ticket Router

A production-oriented, full-stack application that uses AI to analyze, route, and generate responses for customer support tickets. The system leverages the Hugging Face Inference API for all AI tasks and features a modern React frontend and a modular Flask backend.

## Features

*   **AI-Powered Analysis**: Automatically detects the ticket's category, urgency, and sentiment.
*   **Intelligent Routing**: Uses a conditional workflow to assign tickets to the appropriate team (e.g., Priority Support, Technical, Billing).
*   **Contextual Guidance**: Generates either urgent troubleshooting steps or detailed self-service guidance based on the ticket's urgency.
*   **Automated Response Generation**: Creates a professional, empathetic customer-facing email preview for agents.
*   **Modern UI**: A clean, responsive dashboard built with React for a seamless user experience.
*   **Modular Backend**: A scalable, production-ready Flask backend built with a service-oriented architecture.

## Tech Stack

| Area    | Technology                               |
| :------ | :--------------------------------------- |
| **Frontend** | React (with Vite), JavaScript, CSS       |
| **Backend**  | Python, Flask                            |
| **AI Services** | Hugging Face Inference API (via OpenAI-compatible client) |

## Project Structure

The project is organized into two main directories for clear separation of concerns:

```
Gemini_TicketSupporter/
├── backend/      # Contains the Flask API and all related logic
└── frontend/     # Contains the React user interface
```

## Prerequisites

Before you begin, ensure you have the following installed:
*   **Node.js** (v18 or later) and **npm**
*   **Python** (v3.9 or later) and **pip**
*   A **Hugging Face User Access Token** with `read` permissions. You can get one here.

## Setup and Installation

Follow these steps to set up the project locally.

### 1. Backend Setup

First, set up and run the Flask server.

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a Python virtual environment
# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# 3. Install the required Python packages
pip install -r requirements.txt

# 4. Create the environment file
# Create a file named .env in the 'backend' directory and add your Hugging Face token:
HF_API_TOKEN="hf_YourHuggingFaceApiTokenHere"
```

### 2. Frontend Setup

In a new terminal, set up the React client.

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install the required Node.js packages
npm install
```

## Running the Application

You need to run both the backend and frontend servers concurrently in two separate terminals.

*   **Terminal 1: Start the Backend**
    ```bash
    # (Inside the backend/ directory with venv active)
    python app.py
    ```
    The backend will be running at `http://127.0.0.1:5001`.

*   **Terminal 2: Start the Frontend**
    ```bash
    # (Inside the frontend/ directory)
    npm run dev
    ```
    The application will automatically open in your browser at `http://localhost:5173`.