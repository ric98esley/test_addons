from odoo import fields, models


class ProductCrossSell(models.Model):
    _name = "product.cross.sell"
    _description = "Cross Selling Rule"
    _rec_name = "product_id"

    product_id = fields.Many2one(
        "product.product",
        required=True,
        help="The product that triggers the suggestion.",
    )
    suggested_product_id = fields.Many2one(
        "product.product",
        required=True,
        help="The product to be suggested.",
    )
    sequence = fields.Integer(default=10)
    comment = fields.Text()
