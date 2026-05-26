"""
Unit tests for PII detector and masker utilities.
"""
import sys
import os
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pii_detector import PIIDetector, PIIMasker, PIIPatterns


class TestPIIDetector:
    """Test cases for PII detection"""

    def test_detect_email(self):
        """Test email detection"""
        text = "Contact me at john.doe@example.com for support"
        detected = PIIDetector.find_pii(text)
        assert 'emails' in detected
        assert 'john.doe@example.com' in detected['emails']
        print("[PASS] Email detection works")

    def test_detect_phone(self):
        """Test phone number detection"""
        test_cases = [
            "(123) 456-7890",
            "123-456-7890",
            "+1-123-456-7890",
            "123.456.7890"
        ]
        for phone in test_cases:
            text = f"Call me at {phone}"
            detected = PIIDetector.find_pii(text)
            assert 'phone_numbers' in detected, f"Failed to detect: {phone}"
        print("✓ Phone number detection works (all formats)")

    def test_detect_ssn(self):
        """Test SSN detection"""
        test_cases = [
            "123-45-6789",
            "123456789"
        ]
        for ssn in test_cases:
            text = f"My SSN is {ssn}"
            detected = PIIDetector.find_pii(text)
            assert 'ssn' in detected, f"Failed to detect: {ssn}"
        print("✓ SSN detection works (both formats)")

    def test_detect_credit_card(self):
        """Test credit card detection"""
        test_cases = [
            "4532-1234-5678-9010",
            "4532 1234 5678 9010",
            "4532123456789010"
        ]
        for cc in test_cases:
            text = f"Card: {cc}"
            detected = PIIDetector.find_pii(text)
            assert 'credit_cards' in detected, f"Failed to detect: {cc}"
        print("✓ Credit card detection works (multiple formats)")

    def test_detect_account_id(self):
        """Test account ID detection"""
        test_cases = [
            "ACC-123456",
            "ACCT-789012",
            "ACCOUNT-345678",
            "CUST-901234"
        ]
        for acc_id in test_cases:
            text = f"Your account: {acc_id}"
            detected = PIIDetector.find_pii(text)
            assert 'account_ids' in detected, f"Failed to detect: {acc_id}"
        print("✓ Account ID detection works")

    def test_detect_ip_address(self):
        """Test IP address detection"""
        text = "Server IP is 192.168.1.1"
        detected = PIIDetector.find_pii(text)
        assert 'ip_addresses' in detected
        assert '192.168.1.1' in detected['ip_addresses']
        print("✓ IP address detection works")

    def test_has_pii(self):
        """Test has_pii convenience method"""
        text_with_pii = "Email: test@example.com"
        text_without_pii = "This is a normal support ticket"

        assert PIIDetector.has_pii(text_with_pii) is True
        assert PIIDetector.has_pii(text_without_pii) is False
        print("✓ has_pii method works")

    def test_no_false_positives(self):
        """Test that normal text doesn't trigger false positives"""
        text = "I have 4 items in my order. The cost is $123.45. My account is 1 year old."
        detected = PIIDetector.find_pii(text)
        # Should not detect anything significant
        assert len(detected) == 0 or all(k not in detected for k in ['emails', 'phone_numbers', 'ssn'])
        print("✓ No false positives in normal text")


class TestPIIMasker:
    """Test cases for PII masking"""

    def test_mask_email(self):
        """Test email masking"""
        text = "Contact john@example.com"
        masked, detected = PIIMasker.mask_pii(text)
        assert '[EMAIL_MASKED]' in masked
        assert 'john@example.com' not in masked
        assert 'emails' in detected
        print("✓ Email masking works")

    def test_mask_phone(self):
        """Test phone number masking"""
        text = "Call me at (555) 123-4567"
        masked, detected = PIIMasker.mask_pii(text)
        assert '[PHONE_MASKED]' in masked
        assert '555' not in masked.split('[PHONE_MASKED]')[0]
        print("✓ Phone masking works")

    def test_mask_ssn(self):
        """Test SSN masking"""
        text = "SSN: 123-45-6789"
        masked, detected = PIIMasker.mask_pii(text)
        assert '[SSN_MASKED]' in masked
        assert '123-45-6789' not in masked
        print("✓ SSN masking works")

    def test_mask_credit_card(self):
        """Test credit card masking"""
        text = "Card: 4532-1234-5678-9010"
        masked, detected = PIIMasker.mask_pii(text)
        assert '[CREDITCARD_MASKED]' in masked
        assert '4532-1234-5678-9010' not in masked
        print("✓ Credit card masking works")

    def test_mask_multiple_pii(self):
        """Test masking multiple types of PII"""
        text = """
        Customer: John Smith
        Email: john@example.com
        Phone: (555) 123-4567
        SSN: 123-45-6789
        Account: ACC-789012
        """
        masked, detected = PIIMasker.mask_pii(text)

        # Check that all PII types are detected
        assert 'emails' in detected
        assert 'phone_numbers' in detected
        assert 'ssn' in detected
        assert 'account_ids' in detected

        # Check that all are masked
        assert '[EMAIL_MASKED]' in masked
        assert '[PHONE_MASKED]' in masked
        assert '[SSN_MASKED]' in masked
        assert '[ACCOUNT_ID_MASKED]' in masked

        # Check that original values are not in masked text
        assert 'john@example.com' not in masked
        assert '123-45-6789' not in masked

        print("✓ Multiple PII masking works")

    def test_mask_preserves_context(self):
        """Test that masking preserves readability"""
        text = "Email me at support@company.com or call (555) 123-4567 for help"
        masked, detected = PIIMasker.mask_pii(text)

        # Should still be readable
        assert "Email me at [EMAIL_MASKED] or call [PHONE_MASKED] for help" == masked.strip()
        print("✓ Masked text is readable")


class TestIntegration:
    """Integration tests for PII detection workflow"""

    def test_full_workflow(self):
        """Test complete detection and masking workflow"""
        original_ticket = """
        Hello, I'm Jane Doe.
        Email: jane@company.com
        Phone: (555) 987-6543
        Account: ACC-456789
        I can't access my account. Please help!
        """

        # Step 1: Detect
        detected = PIIDetector.find_pii(original_ticket)
        assert len(detected) > 0, "Should detect PII"

        # Step 2: Check has_pii
        assert PIIDetector.has_pii(original_ticket), "has_pii should return True"

        # Step 3: Mask
        masked, _ = PIIMasker.mask_pii(original_ticket)

        # Step 4: Verify masking
        assert '[EMAIL_MASKED]' in masked
        assert '[PHONE_MASKED]' in masked
        assert '[ACCOUNT_ID_MASKED]' in masked
        assert 'jane@company.com' not in masked
        assert '555' not in masked.split('[PHONE_MASKED]')[0]

        print("✓ Full workflow integration test passed")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Running PII Detector Tests")
    print("="*60 + "\n")

    # Test detection
    print("Testing PII Detection:")
    print("-" * 60)
    detector_tests = TestPIIDetector()
    detector_tests.test_detect_email()
    detector_tests.test_detect_phone()
    detector_tests.test_detect_ssn()
    detector_tests.test_detect_credit_card()
    detector_tests.test_detect_account_id()
    detector_tests.test_detect_ip_address()
    detector_tests.test_has_pii()
    detector_tests.test_no_false_positives()

    # Test masking
    print("\nTesting PII Masking:")
    print("-" * 60)
    masker_tests = TestPIIMasker()
    masker_tests.test_mask_email()
    masker_tests.test_mask_phone()
    masker_tests.test_mask_ssn()
    masker_tests.test_mask_credit_card()
    masker_tests.test_mask_multiple_pii()
    masker_tests.test_mask_preserves_context()

    # Integration tests
    print("\nTesting Integration:")
    print("-" * 60)
    integration_tests = TestIntegration()
    integration_tests.test_full_workflow()

    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60 + "\n")
