from odoo import models, fields


class UbicacionReport(models.Model):
    _name = 'ubicacion.report'
    _description = 'Ubicacion Report'
    _auto = False

    name = fields.Char('Title')
    #publisher_id = fields.Many2one('res.partner')
    #date_published = fields.Date()

    def init(self):
        self.env.cr.execute("""
           CREATE OR REPLACE VIEW ubicacion_report AS
           (SELECT *
           FROM ubicacion
           WHERE active = True)
        """)
