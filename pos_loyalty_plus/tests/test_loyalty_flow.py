from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPosLoyaltyPlus(TransactionCase):
    def setUp(self):
        super(TestPosLoyaltyPlus, self).setUp()
        self.user = self.env.user
        self.company = self.user.company_id
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100,
                "available_in_pos": True,
            }
        )

        # Create basic POS Config
        self.pos_config = self.env["pos.config"].create(
            {
                "name": "Test POS",
            }
        )

        # Create payment method
        self.payment_method = self.env["pos.payment.method"].create(
            {
                "name": "Cash",
            }
        )
        self.pos_config.payment_method_ids = [(4, self.payment_method.id)]

        # Open session
        self.pos_session = self.env["pos.session"].create(
            {
                "config_id": self.pos_config.id,
                "user_id": self.user.id,
                "start_at": fields.Datetime.now(),
            }
        )
        self.pos_session.action_pos_session_open()

    def test_loyalty_program_creation(self):
        """Test that setting points per currency creates a loyalty program"""
        self.pos_config.write({"loyalty_points_per_currency": 1.0})
        self.assertTrue(
            self.pos_config.loyalty_program_id, "Loyalty program should be created"
        )
        self.assertEqual(
            self.pos_config.loyalty_program_id.name,
            f"Loyalty Program - {self.pos_config.name}",
        )

        rule = self.pos_config.loyalty_program_id.rule_ids[0]
        self.assertEqual(rule.reward_point_amount, 1.0)
        self.assertEqual(rule.reward_point_mode, "money")

    def test_loyalty_points_accumulation(self):
        """Test points accumulation on order"""
        # Setup loyalty program
        self.pos_config.write({"loyalty_points_per_currency": 1.0})
        program = self.pos_config.loyalty_program_id

        # Create order with points
        # We simulate the data sent from frontend
        order_data = {
            "data": {
                "name": "Order 001",
                "amount_paid": 100,
                "amount_total": 100,
                "amount_tax": 0,
                "amount_return": 0,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "qty": 1,
                            "price_unit": 100,
                            "price_subtotal": 100,
                            "price_subtotal_incl": 100,
                        },
                    ]
                ],
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "payment_method_id": self.payment_method.id,
                            "amount": 100,
                            "payment_date": fields.Date.today(),
                            "name": fields.Datetime.now(),
                        },
                    ]
                ],
                "pos_session_id": self.pos_session.id,
                "partner_id": self.partner.id,
                "user_id": self.env.uid,
                "sequence_number": 1,
                "creation_date": fields.Datetime.to_string(fields.Datetime.now()),
                "fiscal_position_id": False,
                "pricelist_id": self.pos_config.pricelist_id.id,
            }
        }

        # 1. Create order
        order_id = self.env["pos.order"].create_from_ui([order_data])[0]["id"]
        order = self.env["pos.order"].browse(order_id)

        # 2. Simulate coupon data update (points earned)
        coupon_data = {
            -1: {  # New coupon/card
                "program_id": program.id,
                "partner_id": self.partner.id,
                "points": 100,
                "code": "TESTCODE",
            }
        }

        # 3. Call confirm_coupon_programs
        order.confirm_coupon_programs(coupon_data)

        # Verify points on order
        self.assertEqual(
            order.loyalty_points, 100, "Order should have 100 loyalty points"
        )

        # Verify points on partner
        self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.loyalty_points, 100, "Partner should have 100 loyalty points"
        )

        # Verify session total
        self.pos_session.invalidate_recordset()
        self.assertEqual(
            self.pos_session.total_loyalty_points,
            100,
            "Session should have 100 total points",
        )

    def test_loyalty_report_generation(self):
        """Test that the loyalty report can be rendered without errors"""
        # Create some data
        self.pos_config.write({"loyalty_points_per_currency": 1.0})
        program = self.pos_config.loyalty_program_id

        # Create order with points
        order_data = {
            "data": {
                "name": "Order Report Test",
                "amount_paid": 50,
                "amount_total": 50,
                "amount_tax": 0,
                "amount_return": 0,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "qty": 1,
                            "price_unit": 50,
                            "price_subtotal": 50,
                            "price_subtotal_incl": 50,
                        },
                    ]
                ],
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "payment_method_id": self.payment_method.id,
                            "amount": 50,
                            "payment_date": fields.Date.today(),
                            "name": fields.Datetime.now(),
                        },
                    ]
                ],
                "pos_session_id": self.pos_session.id,
                "partner_id": self.partner.id,
                "user_id": self.env.uid,
                "sequence_number": 2,
                "creation_date": fields.Datetime.to_string(fields.Datetime.now()),
                "fiscal_position_id": False,
                "pricelist_id": self.pos_config.pricelist_id.id,
            }
        }
        order_id = self.env["pos.order"].create_from_ui([order_data])[0]["id"]
        order = self.env["pos.order"].browse(order_id)

        coupon_data = {
            -1: {
                "program_id": program.id,
                "partner_id": self.partner.id,
                "points": 50,
                "code": "REPORTCODE",
            }
        }
        order.confirm_coupon_programs(coupon_data)

        self.assertEqual(
            order.loyalty_points, 50, "Order should have 50 points before report"
        )
        self.env.flush_all()

        # Render report
        report = self.env.ref("pos_loyalty_plus.action_report_loyalty_history")
        # We use _render_qweb_html for speed and to avoid wkhtmltopdf dependency in some envs,
        # but _render_qweb_pdf is the real test.
        # If wkhtmltopdf is missing, it might fail. The log said "You need Wkhtmltopdf".
        # So let's try _render_qweb_html first as a sanity check for the template.
        html = report._render_qweb_html(report.id, self.partner.ids)
        self.assertTrue(html, "Report HTML should be generated")
        self.assertIn(b"Order Report Test", html[0], "Report should contain order name")
        self.assertIn(b"50.0", html[0], "Report should contain points")
        self.assertIn(b"50.0", html[0], "Report should contain points")
