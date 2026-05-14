# Copyright 2024 Aybit.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Aybit SMS Provider",
    "summary": "Custom SMS provider for IAP services",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/aybit",
    "author": "Aybit, Odoo Community Association (OCA)",
    "maintainers": [],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["iap_alternative_provider", "sms"],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_template_view.xml",
    ],
}
