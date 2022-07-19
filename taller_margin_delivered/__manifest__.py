# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Taller Margin Delivered",
    "version": "15.0.1.0",
    "author": "Tecnativa,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/margin-analysis",
    "category": "Sales",
    "license": "AGPL-3",
    "depends": [
        "taller",
        "stock",
        "sale_margin_security",
    ],
    "data": [
        "views/taller_margin_view.xml",
        "views/ordenes_reparacion.xml",
        "wizard/taller_margin_wizard.xml"
    ],
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["sergio-teruel"],
}
