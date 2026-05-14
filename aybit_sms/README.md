# Aybit SMS (SMSOrigin Provider)

SMS provider module for Odoo 18.0 using [SMSOrigin](https://processor.smsorigin.com) API.

## Features

- Alternative SMS provider for Odoo IAP system
- Direct integration with SMSOrigin XML API
- Turkish character support (ISO-8859-9)
- Credit balance checking
- Batch SMS sending

## Installation

1. Copy this module to your Odoo addons directory
2. Update your apps list
3. Install the module

## Configuration

1. Go to **Settings > IAP Accounts**
2. Create a new account with Provider **"SMSOrigin (Aybit)"**
3. Enter your SMSOrigin credentials:
   - **Username**: Your SMSOrigin username
   - **Password**: Your SMSOrigin password
   - **Channel Code**: Your channel code (e.g., 376)
   - **Originator**: Sender name (leave empty for panel default)
4. Click **Check Credit** to verify your credentials
5. Set as default SMS account

## Phone Number Format

The module automatically normalizes phone numbers to the `90XXXXXXXXX` format required by SMSOrigin:
- `5309943959` → `905309943959`
- `05309943959` → `905309943959`
- `905309943959` → `905309943959`

## License

AGPL-3
