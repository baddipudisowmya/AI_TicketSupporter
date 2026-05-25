"""
Centralized repository for all LLM prompt templates.

This separation makes it easy to version, test, and refine prompts
without altering the application's core logic.
"""

def get_analysis_prompt(ticket_text):
    """
    Prompt to analyze a ticket and return a structured JSON object.
    """
    return (
        f"You are an expert support ticket analyzer. Analyze the following ticket and return a single JSON object with three keys: 'category', 'urgency', and 'sentiment'.\n"
        f"The possible values are:\n"
        f"- 'category': ['Billing Issue', 'Technical Problem', 'Account Access', 'Product Question', 'General Inquiry']\n"
        f"- 'urgency': ['Urgent', 'High', 'Medium', 'Low']\n"
        f"- 'sentiment': ['Positive', 'Neutral', 'Negative']\n\n"
        f"Ticket: \"{ticket_text}\"\n\n"
        f"JSON Response:"
    )

def get_urgent_guidance_prompt(ticket_text, category):
    """Prompt for generating immediate, critical troubleshooting steps."""
    return (
        f"[INST] You are an expert support engineer. A critical, time-sensitive ticket has arrived.\n"
        f"Provide immediate, concise troubleshooting steps for a support agent to resolve this urgent issue.\n"
        f"Focus on action, not explanation.\n\n"
        f"**Urgent Ticket:** \"{ticket_text}\"\n"
        f"**Category:** {category}\n\n"
        f"**Urgent Troubleshooting Steps:**\n"
        f"[/INST]"
    )

def get_self_service_guidance_prompt(ticket_text, category):
    """Prompt for generating detailed, self-service guidance for standard issues."""
    return (
        f"[INST] You are a helpful support specialist.\n"
        f"Generate detailed, easy-to-follow self-service guidance for the following customer issue.\n"
        f"The goal is to empower the user to solve the problem themselves.\n\n"
        f"**Customer Ticket:** \"{ticket_text}\"\n"
        f"**Category:** {category}\n\n"
        f"**Detailed Self-Service Guidance:**\n"
        f"[/INST]"
    )

def get_email_generation_prompt(ticket_text, analysis, routing_decision):
    """Prompt for generating the final, professional customer-facing email."""
    return (
        f"[INST] You are a world-class customer support agent. Your goal is to write a perfect customer-facing email.\n"
        f"- Be empathetic and professional.\n"
        f"- Acknowledge the customer's issue.\n"
        f"- Inform them their ticket has been routed to the correct team ({routing_decision}).\n"
        f"- Do NOT include the internal troubleshooting steps in the email.\n"
        f"- Keep the email concise and clear.\n\n"
        f"**Original Ticket:** \"{ticket_text}\"\n"
        f"**Analysis:** Category: {analysis['category']}, Urgency: {analysis['urgency']}, Sentiment: {analysis['sentiment']}\n\n"
        f"**Draft the customer response email below:**\n"
        f"[/INST]"
    )