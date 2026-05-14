# Copyright 2024 Aybit.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("aybit", "SMSOrigin (Aybit)")],
        ondelete={"aybit": "cascade"},
    )

    # SMSOrigin API configuration fields
    aybit_username = fields.Char("Username", groups="base.group_system")
    aybit_password = fields.Char("Password", groups="base.group_system")
    aybit_channel_code = fields.Char("Channel Code", groups="base.group_system")
    aybit_originator = fields.Char(
        "Originator",
        help="Sender name/originator. Leave empty to use default from panel.",
    )

    @api.constrains("provider", "aybit_username", "aybit_password", "aybit_channel_code")
    def _check_aybit_credentials(self):
        for record in self:
            if record.provider == "aybit":
                if not record.aybit_username:
                    raise UserError(_("Username is required for SMSOrigin provider"))
                if not record.aybit_password:
                    raise UserError(_("Password is required for SMSOrigin provider"))
                if not record.aybit_channel_code:
                    raise UserError(_("Channel Code is required for SMSOrigin provider"))

    def action_get_aybit_credit(self):
        """Check SMSOrigin credit balance"""
        self.ensure_one()
        if self.provider != "aybit":
            raise UserError(_("This action is only available for SMSOrigin provider"))

        xml_payload = f"""<?xml version="1.0" encoding="ISO-8859-9"?>
<MainReportRoot>
    <Command>6</Command>
    <PlatformID>1</PlatformID>
    <UserName>{self.aybit_username}</UserName>
    <ChannelCode>{self.aybit_channel_code}</ChannelCode>
    <PassWord>{self.aybit_password}</PassWord>
</MainReportRoot>"""

        headers = {"Content-Type": "text/xml; charset=ISO-8859-9"}
        response = requests.post(
            "https://processor.smsorigin.com/xml/process.aspx",
            data=xml_payload.encode("iso-8859-9"),
            headers=headers,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": _("Credit Response: %s") % response.text,
                "type": "info",
                "sticky": True,
            },
        }

    def _get_service_from_provider(self):
        """Return the SMS service for Aybit provider"""
        self.ensure_one()
        if self.provider == "aybit":
            service = self.env["iap.service"].search(
                [("technical_name", "=", "sms")], limit=1
            )
            if not service:
                service = self.env["iap.service"].create(
                    {
                        "name": "SMS",
                        "technical_name": "sms",
                        "description": "SMS Service",
                        "unit_name": "Credits",
                        "integer_balance": True,
                    }
                )
            return service
        return super()._get_service_from_provider()
