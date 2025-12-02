from odoo import api, models


class ReportLoyaltyHistoryPeriod(models.AbstractModel):
    _name = "report.pos_loyalty_plus.report_loyalty_period"
    _description = "Loyalty History Period Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]

        # Search orders with loyalty points in the date range
        orders = self.env["pos.order"].search(
            [
                ("date_order", ">=", start_date),
                ("date_order", "<=", end_date),
                ("loyalty_points", ">", 0),
                ("partner_id", "!=", False),
            ],
            order="partner_id, date_order",
        )

        # Group by partner
        partner_data = {}
        for order in orders:
            partner = order.partner_id
            if partner.id not in partner_data:
                partner_data[partner.id] = {
                    "partner_name": partner.name,
                    "current_balance": partner.loyalty_points,
                    "orders": [],
                    "period_total": 0.0,
                }

            partner_data[partner.id]["orders"].append(
                {
                    "date": order.date_order,
                    "ref": order.name,
                    "points": order.loyalty_points,
                }
            )
            partner_data[partner.id]["period_total"] += order.loyalty_points

        return {
            "doc_ids": docids,
            "doc_model": "pos.loyalty.report.wizard",
            "data": data,
            "start_date": start_date,
            "end_date": end_date,
            "partner_data": partner_data,
        }
