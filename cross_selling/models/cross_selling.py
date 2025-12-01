from odoo import fields, models


class ProductCrossSell(models.Model):
    _name = "product.cross.sell"
    _description = "Optional Product Relation"
    _table = "product_optional_rel"  # <-- usa la tabla existente

    src_id = fields.Many2one("product.template", required=True, ondelete="cascade")
    dest_id = fields.Many2one("product.template", required=True, ondelete="cascade")
