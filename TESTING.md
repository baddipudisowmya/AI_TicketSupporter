# AI Support Ticket Router - Testing Strategy

This document outlines the testing strategy and specific test cases for the AI Support Ticket Router application. The tests are divided into three main categories: Backend API/Integration Tests, Backend Service Unit Tests, and Frontend Component/E2E Tests.

## 1. Backend API & Integration Tests (`/backend`)

These tests focus on the Flask API endpoints, primarily validating input, error handling, and the overall flow.

### Endpoint: `POST /api/ticket`

| Test Case Description | Request Body | Expected Status Code | Expected Response Body |
| :--- | :--- | :--- | :--- |
| **Happy Path** | `{"ticket_text": "I can't access my account."}` | `200 OK` | A full JSON object with `analysis`, `routing`, `agent_guidance`, and `customer_response`. |
| **Empty Body** | `{}` | `400 Bad Request` | `{"error": "ticket_text is a required non-empty field"}` |
| **Missing `ticket_text` key** | `{"other_key": "value"}` | `400 Bad Request` | `{"error": "ticket_text is a required non-empty field"}` |
| **Empty `ticket_text`** | `{"ticket_text": ""}` | `400 Bad Request` | `{"error": "ticket_text is a required non-empty field"}` |
| **Whitespace `ticket_text`** | `{"ticket_text": "   "}` | `400 Bad Request` | `{"error": "ticket_text is a required non-empty field"}` |
| **Exceeds Max Length** | `{"ticket_text": "a" * 2001}` | `400 Bad Request` | `{"error": "ticket_text exceeds maximum length of 2000 characters"}` |
| **Upstream API Failure** | `{"ticket_text": "Valid text"}` | `502 Bad Gateway` | `{"error": "An external API error occurred: ..."}` (Simulated by mocking the LLM client) |

## 2. Backend Service Unit Tests (`/backend/services`)

These tests focus on the core business logic in `ticket_processing_service.py`. The `query_chat_model` function should be mocked to simulate various LLM responses and test the service's orchestration and conditional logic.

### Function: `process_support_ticket(ticket_text)`

#### Test Scenarios

1.  **Successful "Urgent" Workflow:**
    *   **Mock LLM Call 1 (Analysis):** Return `{"category": "Account Access", "urgency": "Urgent", "sentiment": "Negative"}`.
    *   **Assert:**
        *   `get_urgent_guidance_prompt` is called.
        *   The routing decision is `Priority Support Team`.
        *   `get_email_generation_prompt` is called with the correct routing decision.
        *   The final response contains `guidance_type: "Urgent Troubleshooting Steps"`.

2.  **Successful "Self-Service" Workflow:**
    *   **Mock LLM Call 1 (Analysis):** Return `{"category": "Product Question", "urgency": "Low", "sentiment": "Neutral"}`.
    *   **Assert:**
        *   `get_self_service_guidance_prompt` is called.
        *   The routing decision is `Default Queue`.
        *   The final response contains `guidance_type: "Detailed Self-Service Guidance"`.

3.  **Routing Logic Verification:**
    *   Simulate different analysis results and verify the `routing_decision`:
        *   `urgency: 'Urgent'` -> `Priority Support Team`
        *   `sentiment: 'Negative'` -> `Priority Support Team`
        *   `category: 'Technical Problem'` -> `Technical Support`
        *   `category: 'Billing Issue'` -> `Billing Department`
        *   `category: 'General Inquiry'` -> `Default Queue`

4.  **Error Handling: LLM Call 1 (Analysis) Fails:**
    *   **Mock LLM Call 1:** Return an error tuple `(None, {"error": "API Failure"})`.
    *   **Assert:** The service function immediately returns the error without making further LLM calls.

5.  **Error Handling: LLM Call 2 (Guidance) Fails:**
    *   **Mock LLM Call 1:** Return a valid analysis.
    *   **Mock LLM Call 2:** Return an error tuple.
    *   **Assert:** The service function returns the error from the second call.

6.  **Error Handling: Invalid JSON from Analysis:**
    *   **Mock LLM Call 1:** Return a non-JSON string like `"This is not JSON"`.
    *   **Assert:** The function catches the `JSONDecodeError` and returns a specific error: `{"error": "Failed to get a valid analysis from the AI model."}`.

## 3. Frontend Tests (`/frontend`)

These tests ensure the React UI behaves correctly from a user's perspective.

### Component: `App.jsx`

| Test Case Description | User Action | Mock API Response | Expected UI Outcome |
| :--- | :--- | :--- | :--- |
| **Initial Render** | Load the page. | N/A | The page displays the title, textarea, and an enabled "Process Ticket" button. No results or errors are visible. |
| **Empty Submission** | Click "Process Ticket" with an empty textarea. | N/A | An error message "Ticket content cannot be empty." appears. No API call is made. |
| **Successful Submission** | 1. Enter text into the textarea.<br>2. Click "Process Ticket". | `200 OK` with valid result data. | 1. The button becomes disabled and shows "Processing...".<br>2. A loading message appears.<br>3. After the API call resolves, the results are displayed correctly in the `ResultsDisplay` component. |
| **Backend Error** | 1. Enter text.<br>2. Click "Process Ticket". | `502 Bad Gateway` with `{"error": "Upstream error"}`. | 1. The loading state clears.<br>2. An error message "Upstream error" is displayed. |
| **Network Error** | 1. Enter text.<br>2. Click "Process Ticket". | Simulate a failed `fetch` call (e.g., network offline). | 1. The loading state clears.<br>2. A generic error message like "Failed to fetch" is displayed. |

### Component: `GuidanceSteps.jsx`

This component's logic for parsing the guidance text should be unit tested.

| Test Case Description | Input `guidance` Prop | Expected Outcome |
| :--- | :--- | :--- |
| **Standard Numbered List** | `"1. Step One\nThis is the description.\n2. Step Two\nAnother description."` | Two guidance cards are rendered with correct titles ("Step One", "Step Two") and descriptions. |
| **Bolded Titles** | `"**Step One**\nDescription one.\n**Step Two**\nDescription two."` | Two guidance cards are rendered with correct titles and descriptions. |
| **Mixed Formatting** | `"1. First Step\nDescription.\n**Second Step**\nAnother description."` | Two guidance cards are rendered correctly. |
| **No Description** | `"1. Just a title"` | One guidance card is rendered with the title and no description paragraph. |
| **Empty/Invalid String** | `""` or `"Just random text"` | The component should not crash and should render no cards. |