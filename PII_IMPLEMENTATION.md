# PII Detection and Masking Implementation

## Overview

This document describes the Personal Information (PII) detection and masking system implemented in the AI Support Ticket Router application. This system protects user privacy by identifying and masking sensitive information before it's sent to external LLM APIs.

## Components

### 1. Backend PII Detector (`backend/utils/pii_detector.py`)

#### **PIIPatterns Class**
Defines regex patterns for detecting common PII types:
- **Emails**: `user@domain.com` format
- **Phone Numbers**: `(123) 456-7890`, `123-456-7890`, `+1-123-456-7890` formats
- **SSN**: `123-45-6789` or `123456789` format
- **Credit Cards**: 16-digit numbers with optional separators
- **Account IDs**: `ACC-123456`, `CUST-789` formats
- **IP Addresses**: IPv4 format
- **Credit Card Expiry**: `MM/YY` or `MM/YYYY` format

#### **PIIDetector Class**
- `find_pii(text)`: Scans text and returns dictionary of detected PII types with instances
- `has_pii(text)`: Boolean check if text contains any PII
- `get_pii_summary(detected_pii)`: User-friendly summary of detected types

#### **PIIMasker Class**
- `mask_pii(text)`: Replaces all PII with masked tokens like `[EMAIL_MASKED]`, `[PHONE_MASKED]`, etc.
- Returns tuple: `(masked_text, detected_pii_dict)`

### 2. Backend Route Validation (`backend/routes/ticket_routes.py`)

**First Layer of Protection:**
- Detects PII in incoming ticket submissions
- Returns warning to user with detected types and examples
- User must remove sensitive info and resubmit
- Never sends unmasked PII to LLM

**Response when PII detected:**
```json
{
  "warning": "Your ticket contains sensitive personal information",
  "detected_pii_types": ["emails", "phone_numbers"],
  "message": "For your security, personal information should not be included...",
  "examples": {
    "emails": ["john@example.com"],
    "phone_numbers": ["(555) 123-4567"]
  }
}
```

### 3. Backend Service Processing (`backend/services/ticket_processing_service.py`)

**Second Layer of Protection:**
- Masks any remaining PII before sending to LLM API
- Prevents accidental data leakage to external services
- Logs detected PII types (without storing actual values)

### 4. Frontend Detection (`frontend/src/App.jsx`)

**Third Layer of Protection (Client-Side):**
- Detects PII patterns before submission
- Shows warning to user with detected types
- Provides UI feedback with `PIIWarning` component
- Prevents submission if PII detected

**User Interface:**
```
⚠️ Security Warning: Your ticket contains emails, phone_numbers.
Please remove personal information before submitting.

Detected Personal Information:
- emails: john@example.com
- phone_numbers: (555) 123-4567
```

## Implementation Details

### Detection Flow

```
User Submits Ticket
       ↓
[Frontend] Client-side detection
  - Shows warning if PII found
  - User must remove sensitive info
       ↓
[Backend Route] Validation layer
  - Detects PII in POST request
  - Returns warning if found
  - Blocks submission
       ↓
[Service Layer] Processing
  - Masks any remaining PII (defensive)
  - Sends masked text to LLM
```

### Masking Examples

**Original Ticket:**
```
Hello, my name is John Smith.
Email: john@example.com
Phone: (555) 123-4567
Account: ACC-789456
I can't access my account. SSN on file: 123-45-6789
```

**Masked Ticket (sent to LLM):**
```
Hello, my name is John Smith.
Email: [EMAIL_MASKED]
Phone: [PHONE_MASKED]
Account: [ACCOUNT_ID_MASKED]
I can't access my account. SSN on file: [SSN_MASKED]
```

## Security Benefits

### 1. **Privacy Protection**
- Sensitive user data never reaches external LLM APIs
- Reduces data exposure risk

### 2. **Compliance**
- GDPR compliant: Minimizes personal data processing
- CCPA compliant: Users control what info is shared
- HIPAA considerations: Prevents health info exposure

### 3. **Defense in Depth**
- Multiple layers of protection (frontend, route, service)
- Even if one layer fails, others provide protection

### 4. **User Awareness**
- Clear warnings about including sensitive info
- Educates users about support ticket best practices

## Testing

Comprehensive test suite in `backend/tests/test_pii_detector.py`:

### Detection Tests
- Email detection (various formats)
- Phone number detection (7 formats)
- SSN detection (2 formats)
- Credit card detection (3 formats)
- Account ID detection
- IP address detection
- False positive verification

### Masking Tests
- Individual PII type masking
- Multiple PII types masking
- Context preservation after masking

### Integration Tests
- Full workflow from detection to masking

**Run Tests:**
```bash
python backend/tests/test_pii_detector.py
```

**Test Results:**
```
Testing PII Detection: 8/8 tests passed
Testing PII Masking: 6/6 tests passed
Testing Integration: 1/1 tests passed
---
All 15 tests passed!
```

## Configuration

### Disabling PII Detection (Not Recommended)

For development/testing only, you can bypass PII detection by modifying `ticket_routes.py`:

```python
# Comment out in handle_process_ticket():
# detected_pii = PIIDetector.find_pii(ticket_text)
# if detected_pii:
#     return jsonify({...}), 400
```

### Adding New PII Patterns

To detect additional PII types:

1. Add regex pattern to `PIIPatterns` class:
```python
SOCIAL_MEDIA_HANDLE = r'@[\w]{3,20}'
```

2. Add to `find_pii()` method:
```python
'social_media_handles': PIIPatterns.SOCIAL_MEDIA_HANDLE,
```

3. Add masking logic to `mask_pii()` method:
```python
if 'social_media_handles' in detected_pii:
    masked_text = re.sub(
        PIIPatterns.SOCIAL_MEDIA_HANDLE,
        '[HANDLE_MASKED]',
        masked_text
    )
```

## Limitations

### What's Detected
✓ Emails, phone numbers, SSN, credit cards  
✓ Account IDs, IP addresses, credit card expiry  
✓ Well-formatted structured data  

### What's NOT Detected
✗ Misspelled emails (e.g., "john at example.com")  
✗ Unformatted SSN (e.g., "one-two-three four-five six-seven eight-nine")  
✗ Person names (too many false positives)  
✗ Partial/incomplete data  
✗ Custom identifiers without patterns  

## Future Enhancements

1. **Fuzzy Matching**: Detect misspelled/unformatted PII
2. **Machine Learning**: Use ML models for context-aware detection
3. **Audit Logging**: Log PII detection for compliance audits
4. **Data Retention Policy**: Auto-delete sensitive data after X days
5. **User Education**: Add tooltip hints during form input
6. **Custom Patterns**: Allow organizations to define custom PII patterns

## Best Practices

### For Users
- Never include personal information in support tickets
- Use support tickets for technical issues only
- Verify support ticket recipients before submitting
- Remove sensitive data before attaching documents

### For Developers
- Always mask PII before sending to external APIs
- Log detected PII types, not actual values
- Update patterns when new PII types are identified
- Test with real-world data samples
- Monitor masking effectiveness in logs

## Troubleshooting

### Issue: Legitimate data being masked
**Solution**: Check if legitimate data matches PII patterns. Example: Account number "ACC-123456" might trigger account ID masking. This is intentional for safety.

### Issue: PII not being detected
**Solution**: 
- Check data format (patterns expect specific formats)
- Add custom pattern to `PIIPatterns` class
- Run `test_pii_detector.py` to verify detection

### Issue: False positives in error messages
**Solution**: Error messages showing masked data are intentional. Real PII is masked in logs.

## Related Files

- `backend/utils/pii_detector.py` - Core PII detection/masking
- `backend/routes/ticket_routes.py` - Route-level validation
- `backend/services/ticket_processing_service.py` - Service-level masking
- `frontend/src/App.jsx` - Frontend detection and UI
- `backend/tests/test_pii_detector.py` - Test suite
- `SECURITY.md` - Overall security documentation

## Support

For questions or issues with PII detection:
1. Check test cases in `test_pii_detector.py`
2. Review patterns in `PIIPatterns` class
3. Enable debug logging in `pii_detector.py`
4. Consult SECURITY.md for broader context
