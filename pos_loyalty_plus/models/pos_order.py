from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    loyalty_points = fields.Float(
        string="Loyalty Points Earned",
        help="Loyalty points earned in this order.",
        readonly=True,
    )

    @api.model
    def _process_order(self, order, options, draft=False):
        # Override to capture loyalty points from the frontend order data
        order_id = super(PosOrder, self)._process_order(order, options, draft)
        if order_id:
            self.browse(order_id)
        return order_id

    def confirm_coupon_programs(self, coupon_data):
        res = super(PosOrder, self).confirm_coupon_programs(coupon_data)

        for _, data in coupon_data.items():
            # We only care about points earned (positive change)
            if "points" in data and data["points"] > 0:
                pass

        # So we can iterate over coupon_data and sum points.
        points = 0
        for val in coupon_data.values():
            if "points" in val:
                points += val.get("points", 0)

        self.loyalty_points = points
        return res
