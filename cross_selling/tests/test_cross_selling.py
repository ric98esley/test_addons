from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCrossSelling(TransactionCase):
    def setUp(self):
        super(TestCrossSelling, self).setUp()
        self.product_a = self.env["product.product"].create({"name": "Product A"})
        self.product_b = self.env["product.product"].create({"name": "Product B"})
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

        # Create Cross Selling Rule: A -> B
        self.env["product.cross.sell"].create(
            {
                "product_id": self.product_a.id,
                "suggested_product_id": self.product_b.id,
                "sequence": 10,
            }
        )

    def test_cross_selling_wizard(self):

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        wizard = (
            self.env["cross.selling.wizard"]
            .with_context(active_id=order.id)
            .create({"sale_order_id": order.id})
        )

        defaults = (
            self.env["cross.selling.wizard"]
            .with_context(active_id=order.id)
            .default_get(["sale_order_id", "line_ids"])
        )

        self.assertTrue(defaults.get("line_ids"), "Wizard should have suggestions")
        self.assertEqual(len(defaults["line_ids"]), 1, "Should have 1 suggestion")

        suggestion_data = defaults["line_ids"][0][2]  # (0, 0, {data})
        self.assertEqual(
            suggestion_data["product_id"],
            self.product_b.id,
            "Suggestion should be Product B",
        )

        wizard = self.env["cross.selling.wizard"].create(defaults)

        wizard.action_add_suggestions()

        self.assertTrue(
            self.product_b in order.order_line.mapped("product_id"),
            "Product B should be added to the order",
        )
        self.assertEqual(len(order.order_line), 2, "Order should have 2 lines")
