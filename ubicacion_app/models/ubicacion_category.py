from odoo import api, fields, models


class UbicacionCategory(models.Model):
    _name = 'ubicacion.category'
    _description = 'Ubicacion Category'
    _parent_store = True

    name = fields.Char(translate=True, required=True)
    # Hierarchy fields
    parent_id = fields.Many2one(
        'ubicacion.category',
        string='Parent Category',
        ondelete='restrict',
    )
    parent_path = fields.Char(index=True)

    # Optional, but good to have
    child_ids = fields.One2many(
        'ubicacion.category',
        'parent_id',
        string='Subcategories',
    )

    highlighted_id = fields.Reference(
        [('ubicacion', 'Ubicacion'),
         ('res.partner', 'Author')],
        'Category Highlight',
    )
