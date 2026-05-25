"""
Ticket Processing API Routes

This blueprint handles all routes related to ticket submission and processing.
It is responsible for input validation and invoking the appropriate service.
"""
from flask import Blueprint, request, jsonify
from services.ticket_processing_service import process_support_ticket

# Create a Blueprint
ticket_bp = Blueprint('ticket_bp', __name__, url_prefix='/api')

@ticket_bp.route('/ticket', methods=['POST'])
def handle_process_ticket():
    """
    API endpoint to process a new support ticket.
    It validates the input and passes it to the ticket processing service.
    """
    data = request.get_json()
    # --- Input Validation ---
    if not data or not data.get('ticket_text') or not data['ticket_text'].strip():
        return jsonify({"error": "ticket_text is a required non-empty field"}), 400

    ticket_text = data['ticket_text']
    if len(ticket_text) > 2000:
        return jsonify({"error": "ticket_text exceeds maximum length of 2000 characters"}), 400

    result, error = process_support_ticket(ticket_text)
    
    if error:
        return jsonify(error), 502 # 502 Bad Gateway indicates an upstream API error
    
    return jsonify(result)