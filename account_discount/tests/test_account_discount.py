from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountDiscount(TransactionCase):
    def setUp(self):
        super(TestAccountDiscount, self).setUp()

        # Get the company and configure accounting
        self.company = self.env.company

        # Create accounts needed for invoices
        self.account_receivable = self.env["account.account"].create(
            {
                "code": "TEST.REC",
                "name": "Test Receivable",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )

        self.account_payable = self.env["account.account"].create(
            {
                "code": "TEST.PAY",
                "name": "Test Payable",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )

        self.account_revenue = self.env["account.account"].create(
            {
                "code": "TEST.REV",
                "name": "Test Revenue",
                "account_type": "income",
            }
        )

        # Set the default accounts on the company
        self.company.write(
            {
                "account_sale_tax_id": False,
                "account_purchase_tax_id": False,
            }
        )

        # Set the property fields for partners
        self.env["ir.property"]._set_default(
            "property_account_receivable_id",
            "res.partner",
            self.account_receivable,
            self.company,
        )
        self.env["ir.property"]._set_default(
            "property_account_payable_id",
            "res.partner",
            self.account_payable,
            self.company,
        )

        # Create a sales journal
        self.journal = self.env["account.journal"].create(
            {
                "name": "Test Sales Journal",
                "code": "TSALE",
                "type": "sale",
            }
        )

        # Setup partner types and partners

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
        product_template = self.env["product.template"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        self.product = product_template.product_variant_ids[0]

    def test_discount_application_vip(self):
        """Test that discount is applied for VIP partners"""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_vip.id,
                "journal_id": self.journal.id,
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
                            "account_id": self.account_revenue.id,
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
                "journal_id": self.journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                        },
                    )
                ],
            }
        )
        invoice.invoice_line_ids._compute_discount()
        self.assertEqual(
            invoice.invoice_line_ids[0].discount, 0.0, "Discount should be 0%"
        )
