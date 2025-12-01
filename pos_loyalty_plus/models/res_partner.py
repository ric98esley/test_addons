from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    loyalty_points = fields.Float(
        compute="_compute_loyalty_points",
        help="Total loyalty points accumulated by the customer.",
    )

    def _compute_loyalty_points(self):
        for partner in self:
            # Sum points from all loyalty cards associated with the partner
            cards = self.env["loyalty.card"].search([("partner_id", "=", partner.id)])
            partner.loyalty_points = sum(cards.mapped("points"))

    def action_view_loyalty_points(self):
        self.ensure_one()
        return {
            "name": "Loyalty Cards",
            "type": "ir.actions.act_window",
            "res_model": "loyalty.card",
            "view_mode": "tree,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
