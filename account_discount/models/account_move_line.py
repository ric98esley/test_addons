from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        related="move_id.partner_id",
    )

    partner_type_id = fields.Many2one(
        "res.partner.type",
        string="Partner Type",
        related="partner_id.partner_type_id",
        store=True,
    )

    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        default=0.0,
        compute="_compute_discount",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id", "partner_type_id", "move_id.move_type")
    def _compute_discount(self):
        for line in self:
            if line.partner_type_id and line.move_id.move_type == "out_invoice":
                line.discount = line.partner_type_id.percentage
            else:
                line.discount = 0.0
