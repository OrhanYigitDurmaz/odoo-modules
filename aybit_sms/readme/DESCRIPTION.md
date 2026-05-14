# Aybit SMS Provider

SMS provider module for Odoo using the SMSOrigin API (processor.smsorigin.com).

## Features

- Alternative SMS provider for Odoo IAP system
- Direct integration with SMSOrigin XML API
- Turkish character support (ISO-8859-9 encoding)
- Credit balance checking
- Automatic phone number normalization to 90XXXXXXXXX format
- Batch SMS sending capability

## Configuration

1. Go to Settings > IAP Accounts
2. Create a new account with Provider "SMSOrigin (Aybit)"
3. Enter your SMSOrigin credentials:
   - Username
   - Password
   - Channel Code
   - Originator (optional sender name)
4. Use the "Check Credit" button to verify credentials
5. Set as default SMS account
