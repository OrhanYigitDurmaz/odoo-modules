# Copyright 2024 Aybit.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import _

_logger = logging.getLogger(__name__)

# SMSOrigin API endpoint
SMSORIGIN_URL = "https://processor.smsorigin.com/xml/process.aspx"


class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _send_sms_split(self, numbers_split):
        """Override to send SMS via SMSOrigin provider instead of Odoo IAP"""
        iap_account = self._get_iap_account()
        if iap_account and iap_account.provider == "aybit":
            return self._send_sms_smsorigin(numbers_split, iap_account)
        return super()._send_sms_split(numbers_split)

    def _send_sms_smsorigin(self, numbers_split, iap_account):
        """Send SMS via SMSOrigin API"""
        results = []
        numbers_str = ",".join(
            self._normalize_number(n) for n in numbers_split
        )

        try:
            response = self._send_smsorigin_batch(
                numbers_str, self.content, iap_account
            )
            _logger.info(
                "SMS sent via SMSOrigin. Numbers: %s, Response: %s",
                numbers_str,
                response,
            )
            # All numbers are considered sent if no exception
            results = list(numbers_split)
        except Exception as e:
            _logger.error("Failed to send SMS via SMSOrigin: %s", e)
            # Mark all as failed
            for number in numbers_split:
                self._postprocess_iap_send_sms(
                    None, {number: str(e)}, number=number, content=self.content
                )

        return results

    def _normalize_number(self, number):
        """Normalize phone number to 90XXXXXXXXX format"""
        # Remove spaces, dashes, parentheses
        clean = number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        # Add 90 prefix if missing and starting with 0
        if clean.startswith("0"):
            clean = "90" + clean[1:]
        elif not clean.startswith("90"):
            clean = "90" + clean
        return clean

    def _send_smsorigin_batch(self, numbers, message, iap_account):
        """Send SMS via SMSOrigin API (SmsToMany)

        Args:
            numbers: Comma-separated phone numbers
            message: SMS content
            iap_account: IAP account with SMSOrigin credentials

        Returns:
            Response text from API
        """
        originator = iap_account.aybit_originator or ""

        # XML payload according to SMSOrigin API documentation
        xml_payload = f"""<?xml version="1.0" encoding="ISO-8859-9"?>
<MainmsgBody>
    <Command>0</Command>
    <PlatformID>1</PlatformID>
    <UserName>{iap_account.aybit_username}</UserName>
    <PassWord>{iap_account.aybit_password}</PassWord>
    <ChannelCode>{iap_account.aybit_channel_code}</ChannelCode>
    <Mesgbody>{message}</Mesgbody>
    <Numbers>{numbers}</Numbers>
    <Type>1</Type>
    <Originator>{originator}</Originator>
    <SDate></SDate>
    <EDate></EDate>
    <Concat>1</Concat>
</MainmsgBody>"""

        headers = {"Content-Type": "text/xml; charset=ISO-8859-9"}
        response = requests.post(
            SMSORIGIN_URL,
            data=xml_payload.encode("iso-8859-9"),
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def _get_iap_account(self):
        """Get the IAP account to use for sending SMS"""
        param = self.env["ir.config_parameter"].sudo()
        account_id = param.get_param("sms.iap_account_id")
        if account_id:
            return self.env["iap.account"].browse(int(account_id))
        return None
