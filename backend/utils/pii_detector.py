"""
PII Detection and Masking Utility

This module provides utilities for detecting and masking personally identifiable
information (PII) in support tickets before they are sent to external LLM APIs.
"""
import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PIIPatterns:
    """Regex patterns for detecting common PII types"""

    # Email addresses: user@domain.com
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    # Phone numbers: (123) 456-7890, 123-456-7890, 123.456.7890, +1-123-456-7890
    PHONE = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'

    # SSN: 123-45-6789 or 123456789
    SSN = r'\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b'

    # Credit card: 16 digits with optional spaces/dashes
    CREDIT_CARD = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'

    # Account/Customer IDs: ACC-123456, CUST-789, etc.
    ACCOUNT_ID = r'\b(?:ACC|ACCT|ACCOUNT|CUST|CUSTOMER)[-\s]?[\dA-Z]{6,}\b'

    # IP addresses: 192.168.1.1
    IP_ADDRESS = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

    # Credit card expiry: MM/YY or MM/YYYY
    CREDIT_CARD_EXPIRY = r'\b(?:0[1-9]|1[0-2])/(?:[0-9]{2}|[0-9]{4})\b'

    # US Social Security Number (alternative pattern with dashes)
    SSN_ALT = r'\b\d{3}-\d{2}-\d{4}\b'


class PIIDetector:
    """Detects PII in text"""

    @staticmethod
    def find_pii(text: str) -> Dict[str, List[str]]:
        """
        Scan text for PII and return detected instances.

        Args:
            text: The text to scan for PII

        Returns:
            Dictionary with PII types as keys and lists of found instances as values
        """
        findings = {}

        patterns = {
            'emails': PIIPatterns.EMAIL,
            'phone_numbers': PIIPatterns.PHONE,
            'ssn': PIIPatterns.SSN,
            'credit_cards': PIIPatterns.CREDIT_CARD,
            'account_ids': PIIPatterns.ACCOUNT_ID,
            'ip_addresses': PIIPatterns.IP_ADDRESS,
            'credit_card_expiry': PIIPatterns.CREDIT_CARD_EXPIRY,
        }

        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
                logger.warning(f"Detected {pii_type}: {len(matches)} instance(s)")

        return findings

    @staticmethod
    def has_pii(text: str) -> bool:
        """Check if text contains any PII"""
        return bool(PIIDetector.find_pii(text))

    @staticmethod
    def get_pii_summary(detected_pii: Dict[str, List[str]]) -> str:
        """Generate a user-friendly summary of detected PII"""
        if not detected_pii:
            return ""

        types = list(detected_pii.keys())
        return f"Detected: {', '.join(types)}"


class PIIMasker:
    """Masks PII in text before sending to external APIs"""

    @staticmethod
    def mask_pii(text: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Mask all PII in text and return both masked text and detected PII.

        Args:
            text: The text to mask

        Returns:
            Tuple of (masked_text, detected_pii_dict)
        """
        detected_pii = PIIDetector.find_pii(text)
        masked_text = text

        # Mask emails
        if 'emails' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.EMAIL,
                '[EMAIL_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask phone numbers
        if 'phone_numbers' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.PHONE,
                '[PHONE_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask SSN
        if 'ssn' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.SSN,
                '[SSN_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask credit cards
        if 'credit_cards' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.CREDIT_CARD,
                '[CREDITCARD_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask account IDs
        if 'account_ids' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.ACCOUNT_ID,
                '[ACCOUNT_ID_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask IP addresses
        if 'ip_addresses' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.IP_ADDRESS,
                '[IP_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        # Mask credit card expiry
        if 'credit_card_expiry' in detected_pii:
            masked_text = re.sub(
                PIIPatterns.CREDIT_CARD_EXPIRY,
                '[EXPIRY_MASKED]',
                masked_text,
                flags=re.IGNORECASE
            )

        if detected_pii:
            logger.info(f"Masked PII in text. Detected types: {list(detected_pii.keys())}")

        return masked_text, detected_pii
