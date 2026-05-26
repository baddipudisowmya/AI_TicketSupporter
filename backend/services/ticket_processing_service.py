"""
Ticket Processing Service

This service contains the core business logic for orchestrating the AI workflow
for a support ticket. It uses utility functions and prompt templates to perform
its tasks.
"""
import logging
import json
from utils.hf_api_client import query_chat_model, LLM_MODEL
from utils.pii_detector import PIIMasker
from prompts import prompt_templates

def process_support_ticket(ticket_text):
    """
    Orchestrates the full 3-call LLM workflow for analyzing and responding to a ticket.
    """
    # === Mask any remaining PII before processing ===
    masked_ticket_text, detected_pii = PIIMasker.mask_pii(ticket_text)
    if detected_pii:
        logging.warning(f"PII detected and masked in ticket: {list(detected_pii.keys())}")
        ticket_text = masked_ticket_text

    # === LLM Call 1: Analyze Support Ticket ===
    logging.info("Initiating LLM Call 1: Ticket Analysis")
    analysis_prompt = prompt_templates.get_analysis_prompt(ticket_text)
    analysis_messages = [{"role": "user", "content": analysis_prompt}]
    analysis_json_str, error = query_chat_model(analysis_messages, LLM_MODEL, is_json=True)
    if error:
        return None, error
    try:
        analysis = json.loads(analysis_json_str)
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON from analysis model: {analysis_json_str}")
        return None, {"error": "Failed to get a valid analysis from the AI model."}
    logging.info(f"Analysis complete: {analysis}")

    # === LLM Call 2: Conditional Guidance Generation ===
    logging.info("Initiating LLM Call 2: Conditional Guidance Generation")
    if analysis['urgency'] == 'Urgent':
        guidance_prompt = prompt_templates.get_urgent_guidance_prompt(ticket_text, analysis['category'])
        guidance_type = "Urgent Troubleshooting Steps"
    else:
        guidance_prompt = prompt_templates.get_self_service_guidance_prompt(ticket_text, analysis['category'])
        guidance_type = "Detailed Self-Service Guidance"

    guidance_messages = [{"role": "user", "content": guidance_prompt}]
    agent_guidance, error = query_chat_model(guidance_messages, LLM_MODEL)
    if error:
        return None, error
    logging.info("Guidance generated.")

    # --- If/Else Workflow Routing ---
    urgency = analysis.get('urgency')
    sentiment = analysis.get('sentiment')
    category = analysis.get('category')
    if urgency == 'Urgent' or sentiment == 'Negative':
        routing_decision = "Priority Support Team"
    elif category == 'Technical Problem':
        routing_decision = "Technical Support"
    elif category == 'Billing Issue':
        routing_decision = "Billing Department"
    elif category == 'General Inquiry':
        routing_decision = "Default Queue"
    else:
        routing_decision = "Default Queue"

    # === LLM Call 3: Generate Final Customer Email ===
    logging.info("Initiating LLM Call 3: Final Email Generation")
    email_prompt = prompt_templates.get_email_generation_prompt(ticket_text, analysis, routing_decision)
    email_messages = [{"role": "user", "content": email_prompt}]
    customer_email_preview, error = query_chat_model(email_messages, LLM_MODEL)
    if error:
        return None, error
    logging.info("Customer email preview generated.")

    # --- Final Response Assembly ---
    response_data = {
        "analysis": analysis,
        "routing": {"decision": routing_decision},
        "agent_guidance": {"type": guidance_type, "guidance": agent_guidance},
        "customer_response": {"email_preview": customer_email_preview}
    }
    
    return response_data, None