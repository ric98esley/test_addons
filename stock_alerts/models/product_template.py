from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    minimum_stock = fields.Float(
        default=0.0,
        help="Minimum stock level. An alert will be generated"
        " when available quantity falls below this threshold.",
    )
    stock_below_minimum = fields.Boolean(
        compute="_compute_stock_below_minimum",
        search="_search_stock_below_minimum",
        store=False,
        help="Indicates if current stock is below the minimum threshold",
    )

    @api.depends("qty_available", "minimum_stock")
    def _compute_stock_below_minimum(self):
        """Compute if stock is below minimum threshold"""
        for product in self:
            product.stock_below_minimum = (
                product.type == "product"
                and product.minimum_stock > 0
                and product.qty_available < product.minimum_stock
            )

            if product.stock_below_minimum:
                product.message_post(
                    body=f"Stock is below minimum threshold: {product.minimum_stock}",
                    subject=_("Stock Alert"),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )

    def _search_stock_below_minimum(self, operator, value):
        """
        Search method for stock_below_minimum computed field
        Allows filtering products with critical stock in views
        """
        # Get all storable products with minimum stock set
        products = self.search([("type", "=", "product"), ("minimum_stock", ">", 0)])

        # Filter based on the condition
        critical_products = products.filtered(
            lambda p: p.qty_available < p.minimum_stock
        )

        # Handle different operators
        if (operator == "=" and value) or (operator == "!=" and not value):
            # Looking for critical products
            return [("id", "in", critical_products.ids)]
        else:
            # Looking for non-critical products
            return [("id", "not in", critical_products.ids)]

    def get_critical_stock_products(self):
        """
        Returns products with stock below minimum threshold
        Used by the dashboard and automated alert system
        """
        products = self.search(
            [
                ("type", "=", "product"),
                ("minimum_stock", ">", 0),
            ]
        )
        return products.filtered(lambda p: p.qty_available < p.minimum_stock)

    def check_and_create_alerts(self):
        """
        Check stock levels and create alerts for products below minimum
        Called by scheduled action (cron job)
        """
        AlertHistory = self.env["stock.alert.history"]
        critical_products = self.get_critical_stock_products()

        for product in critical_products:
            # Check if there's already an unresolved alert for this product
            existing_alert = AlertHistory.search(
                [
                    ("product_id", "=", product.id),
                    ("resolved", "=", False),
                ],
                limit=1,
            )

            if not existing_alert:
                # Create new alert
                AlertHistory.create(
                    {
                        "product_id": product.id,
                        "qty_available": product.qty_available,
                        "minimum_stock": product.minimum_stock,
                    }
                )

                # Post message to product's chatter
                product.message_post(
                    body=f"""
                        <p><strong>⚠️ Stock Alert: Critical Stock Level</strong></p>
                        <ul>
                            <li>Product: {product.name}</li>
                            <li>Current Stock: {product.qty_available}
                             {product.uom_id.name}</li>
                            <li>Minimum Stock: {product.minimum_stock}
                             {product.uom_id.name}</li>
                            <li>Category: {product.categ_id.name}</li>
                        </ul>
                        <p>Please replenish stock as soon as possible.</p>
                    """,
                    subject=f"Stock Alert: {product.name}",
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )

        # Check if any previously critical products have been resolved
        AlertHistory.check_resolved_alerts()

        return True
