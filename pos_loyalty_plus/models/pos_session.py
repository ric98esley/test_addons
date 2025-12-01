from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    total_loyalty_points = fields.Float(
        compute="_compute_total_loyalty_points",
        help="Total loyalty points accumulated in this session.",
    )

    def _compute_total_loyalty_points(self):
        for session in self:
            # Sum points from all orders in the session
            # Note: We need to ensure pos.order has loyalty_points field
            orders = self.env["pos.order"].search([("session_id", "=", session.id)])
            session.total_loyalty_points = sum(orders.mapped("loyalty_points"))
