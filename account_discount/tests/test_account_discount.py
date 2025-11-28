from odoo.tests import TransactionCase, tagged


@tagged("post_install", "at_install", "account_discount")
class TestAccountDiscount(TransactionCase):
    def setUp(self):
        super(TestAccountDiscount, self).setUp()
        self.partner_type_vip = self.env["res.partner.type"].create(
            {
                "name": "VIP",
                "percentage": 10.0,
            }
        )
        self.partner_vip = self.env["res.partner"].create(
            {
                "name": "VIP Partner",
                "partner_type_id": self.partner_type_vip.id,
            }
        )
        self.partner_normal = self.env["res.partner"].create(
            {
                "name": "Normal Partner",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
            }
        )

    def test_discount_application_vip(self):
        """Test that discount is applied for VIP partners"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_vip.id,
            }
        )
        invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        },
                    )
                ]
            }
        )
        invoice.invoice_line_ids._compute_discount()
        self.assertEqual(
            invoice.invoice_line_ids[0].discount, 10.0, "Discount should be 10%"
        )

    def test_discount_application_normal(self):
        """Test that no discount is applied for partners without type"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_normal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        invoice.invoice_line_ids._compute_discount()
        self.assertEqual(
            invoice.invoice_line_ids[0].discount, 0.0, "Discount should be 0%"
        )
