from odoo import fields, models


class StockAlertHistory(models.Model):
    _name = "stock.alert.history"
    _description = "Stock Alert History"
    _order = "alert_date desc"

    product_id = fields.Many2one(
        "product.template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    alert_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    qty_available = fields.Float(
        help="Quantity available when the alert was generated",
    )
    minimum_stock = fields.Float(
        help="Minimum stock level configured at time of alert",
    )
    resolved = fields.Boolean(
        default=False,
        help="Alert is resolved when stock returns above minimum threshold",
    )
    resolved_date = fields.Datetime(
        help="Date when stock was replenished above minimum",
    )
    category_id = fields.Many2one(
        "product.category",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )

    def check_resolved_alerts(self):
        """
        Check if any unresolved alerts should be marked as resolved
        Called by the scheduled action after creating new alerts
        """
        unresolved_alerts = self.search([("resolved", "=", False)])

        for alert in unresolved_alerts:
            prod = alert.product_id
            # Check if stock is now above minimum
            if prod.qty_available >= prod.minimum_stock:
                alert.write(
                    {
                        "resolved": True,
                        "resolved_date": fields.Datetime.now(),
                    }
                )

                # Post resolution message to product
                qty = prod.qty_available
                min = prod.minimum_stock
                uom = prod.uom_id.name
                prod.message_post(
                    body=f"""
                        <p><strong>✅ Stock Alert Resolved</strong></p>
                        <ul>
                            <li>Product: {prod.name}</li>
                            <li>Current Stock: {qty} {uom}</li>
                            <li>Minimum Stock: {min} {uom}</li>
                        </ul>
                        <p>Stock level is now above minimum threshold.</p>
                    """,
                    subject=f"Stock Alert Resolved: {prod.name}",
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )

        return True
