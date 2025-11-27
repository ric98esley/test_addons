from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        default=0.0,
        compute="_compute_discount",
        store=True,
        readonly=False,
        precompute=True,
    )

    @api.depends("move_id.partner_id", "move_id.move_type")
    def _compute_discount(self):
        for line in self:
            partner = line.move_id.partner_id
            if partner.partner_type_id and line.move_id.move_type == "out_invoice":
                line.discount = partner.partner_type_id.percentaje
            else:
                line.discount = 0.0
