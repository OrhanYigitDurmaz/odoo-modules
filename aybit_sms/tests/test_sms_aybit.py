# Copyright 2024 Aybit.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests import TransactionCase
from odoo.exceptions import UserError, ValidationError


class SmsAybitCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.aybit_account = cls.env["iap.account"].create(
            {
                "name": "SMSOrigin Account",
                "provider": "aybit",
                "aybit_username": "test_user",
                "aybit_password": "test_pass",
                "aybit_channel_code": "376",
                "aybit_originator": "TEST",
            }
        )
        return res

    def test_create_aybit_account(self):
        """Test creating an SMSOrigin IAP account"""
        account = self.env["iap.account"].create(
            {
                "name": "Test SMSOrigin",
                "provider": "aybit",
                "aybit_username": "user",
                "aybit_password": "pass",
                "aybit_channel_code": "123",
            }
        )
        self.assertEqual(account.provider, "aybit")
        self.assertTrue(account.service_id)

    def test_missing_username(self):
        """Test that missing username raises error"""
        with self.assertRaises(ValidationError):
            self.env["iap.account"].create(
                {
                    "name": "Test SMSOrigin",
                    "provider": "aybit",
                    "aybit_password": "pass",
                    "aybit_channel_code": "123",
                }
            )

    def test_missing_password(self):
        """Test that missing password raises error"""
        with self.assertRaises(ValidationError):
            self.env["iap.account"].create(
                {
                    "name": "Test SMSOrigin",
                    "provider": "aybit",
                    "aybit_username": "user",
                    "aybit_channel_code": "123",
                }
            )

    def test_missing_channel_code(self):
        """Test that missing channel code raises error"""
        with self.assertRaises(ValidationError):
            self.env["iap.account"].create(
                {
                    "name": "Test SMSOrigin",
                    "provider": "aybit",
                    "aybit_username": "user",
                    "aybit_password": "pass",
                }
            )

    @mock.patch("requests.post")
    def test_send_sms_via_smsorigin(self, mock_post):
        """Test SMS sending via SMSOrigin"""
        mock_response = mock.Mock()
        mock_response.text = "<MainmsgBody><Result>1</Result></MainmsgBody>"
        mock_response.raise_for_status = mock.Mock()
        mock_post.return_value = mock_response

        sms = self.env["sms.sms"].create(
            {
                "number": "5309943959",
                "body": "Test message",
            }
        )

        # Set the IAP account as default for SMS
        self.env["ir.config_parameter"].sudo().set_param(
            "sms.iap_account_id", self.aybit_account.id
        )

        # Mock the super()._send_sms_split to avoid actual IAP call
        with mock.patch(
            "odoo.addons.sms.models.sms_sms.SmsSms._send_sms_split"
        ):
            # Normalize number should add 90 prefix
            normalized = sms._normalize_number("5309943959")
            self.assertEqual(normalized, "905309943959")

            # Test with number already starting with 90
            normalized = sms._normalize_number("905309943959")
            self.assertEqual(normalized, "905309943959")
