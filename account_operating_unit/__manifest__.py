# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Accounting with Operating Units",
    "summary": "Introduces Operating Unit (OU) in invoices and "
    "Accounting Entries with clearing account",
    "version": "15.0.1.0.1",
    "author": "ForgeFlow, "
    "Serpent Consulting Services Pvt. Ltd.,"
    "WilldooIT Pty Ltd,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Accounting & Finance",
    "depends": ["account","account_reports","analytic_operating_unit"],
    "license": "LGPL-3",
    "data": [
        "security/account_security.xml",
        "views/account_move_view.xml",
        "views/account_journal_view.xml",
        "views/company_view.xml",
        "views/account_payment_view.xml",
        "views/account_invoice_report_view.xml",
        "views/search_template_view.xml",
        "views/report_financial.xml",
        "views/report_trialbalance.xml",
        "views/account_report_view.xml",
        "wizards/account_report_common_view.xml",
    ],
}
