from odoo.tests.common import TransactionCase


class TestStockAlerts(TransactionCase):
    def setUp(self):
        super(TestStockAlerts, self).setUp()

        # Get models
        self.product_model = self.env["product.template"]
        self.alert_history_model = self.env["stock.alert.history"]
        self.category_model = self.env["product.category"]

        # Create test category
        self.test_category = self.category_model.create(
            {
                "name": "Test Category for Alerts",
            }
        )

        # Create test products
        self.product_critical = self.product_model.create(
            {
                "name": "Test Product - Critical Stock",
                "type": "product",
                "categ_id": self.test_category.id,
                "minimum_stock": 100.0,
                "list_price": 50.0,
            }
        )

        self.product_ok = self.product_model.create(
            {
                "name": "Test Product - OK Stock",
                "type": "product",
                "categ_id": self.test_category.id,
                "minimum_stock": 50.0,
                "list_price": 75.0,
            }
        )

        self.product_no_minimum = self.product_model.create(
            {
                "name": "Test Product - No Minimum",
                "type": "product",
                "categ_id": self.test_category.id,
                "minimum_stock": 0.0,
                "list_price": 100.0,
            }
        )

        # Update stock levels using inventory adjustment
        self._set_product_stock(self.product_critical, 50.0)  # Below minimum
        self._set_product_stock(self.product_ok, 100.0)  # Above minimum
        self._set_product_stock(
            self.product_no_minimum, 10.0
        )  # Has stock but no minimum

    def _set_product_stock(self, product, quantity):
        """Helper method to set product stock quantity"""
        # Get the product variant
        product_variant = product.product_variant_ids[0]

        # Get the stock location
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        location = warehouse.lot_stock_id

        # Create inventory adjustment
        inventory = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": product_variant.id,
                    "location_id": location.id,
                    "inventory_quantity": quantity,
                }
            )
        )
        inventory.action_apply_inventory()

    def test_compute_stock_below_minimum(self):
        """Test the computed field stock_below_minimum"""
        # Refresh products to get updated computed fields

        # Product with stock below minimum should be flagged
        self.assertTrue(
            self.product_critical.stock_below_minimum,
            "Product with stock (50) below minimum (100) should be flagged as critical",
        )

        # Product with stock above minimum should not be flagged
        self.assertFalse(
            self.product_ok.stock_below_minimum,
            "Product with stock (100) above minimum (50) should not be flagged",
        )

        # Product without minimum stock should not be flagged
        self.assertFalse(
            self.product_no_minimum.stock_below_minimum,
            "Product without minimum stock should not be flagged",
        )

    def test_get_critical_stock_products(self):
        """Test retrieving products with critical stock levels"""
        critical_products = self.product_model.get_critical_stock_products()

        # Should include product_critical
        self.assertIn(
            self.product_critical,
            critical_products,
            "Critical product should be in the results",
        )

        # Should not include product_ok or product_no_minimum
        self.assertNotIn(
            self.product_ok,
            critical_products,
            "Product with OK stock should not be included",
        )
        self.assertNotIn(
            self.product_no_minimum,
            critical_products,
            "Product without minimum should not be included",
        )

    def test_alert_generation(self):
        """Test that alerts are generated for critical stock"""
        # Clear any existing alerts
        self.alert_history_model.search([]).unlink()

        # Run the alert check
        self.product_model.check_and_create_alerts()

        # Check that alert was created for critical product
        alert = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )

        self.assertTrue(alert, "Alert should be created for critical product")
        self.assertEqual(len(alert), 1, "Should create exactly one alert")
        self.assertFalse(alert.resolved, "New alert should not be resolved")
        self.assertEqual(
            alert.qty_available,
            self.product_critical.qty_available,
            "Alert should record current stock level",
        )
        self.assertEqual(
            alert.minimum_stock,
            self.product_critical.minimum_stock,
            "Alert should record minimum stock threshold",
        )

    def test_no_alert_for_ok_stock(self):
        """Test that no alerts are generated for products with adequate stock"""
        # Clear any existing alerts
        self.alert_history_model.search([]).unlink()

        # Run the alert check
        self.product_model.check_and_create_alerts()

        # Check that no alert was created for OK product
        alert_ok = self.alert_history_model.search(
            [("product_id", "=", self.product_ok.id)]
        )
        self.assertFalse(
            alert_ok, "No alert should be created for product with OK stock"
        )

        # Check that no alert was created for product without minimum
        alert_no_min = self.alert_history_model.search(
            [("product_id", "=", self.product_no_minimum.id)]
        )
        self.assertFalse(
            alert_no_min, "No alert should be created for product without minimum stock"
        )

    def test_duplicate_alert_prevention(self):
        """Test that duplicate alerts are not created"""
        # Clear any existing alerts
        self.alert_history_model.search([]).unlink()

        # Run the alert check first time
        self.product_model.check_and_create_alerts()

        # Count alerts
        alerts_first = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )
        self.assertEqual(len(alerts_first), 1, "Should create one alert on first run")

        # Run the alert check again
        self.product_model.check_and_create_alerts()

        # Count alerts again
        alerts_second = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )
        self.assertEqual(
            len(alerts_second),
            1,
            "Should not create duplicate alert when stock is still critical",
        )

    def test_alert_resolution(self):
        """Test that alerts are resolved when stock is replenished"""
        # Clear any existing alerts
        self.alert_history_model.search([]).unlink()

        # Generate initial alert
        self.product_model.check_and_create_alerts()

        alert = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )
        self.assertTrue(alert, "Alert should be created")
        self.assertFalse(alert.resolved, "Alert should not be resolved initially")

        # Replenish stock above minimum
        self._set_product_stock(self.product_critical, 150.0)

        # Run alert check again
        self.product_model.check_and_create_alerts()

        # Check that alert is now resolved
        self.assertTrue(
            alert.resolved, "Alert should be resolved after stock replenishment"
        )
        self.assertIsNotNone(alert.resolved_date, "Resolved date should be set")

    def test_new_alert_after_resolution(self):
        """Test that a new alert can be created after previous one is resolved"""
        # Clear any existing alerts
        self.alert_history_model.search([]).unlink()

        # Generate initial alert
        self.product_model.check_and_create_alerts()
        initial_alerts = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )
        self.assertEqual(len(initial_alerts), 1, "Should have one initial alert")

        # Replenish stock to resolve alert
        self._set_product_stock(self.product_critical, 150.0)
        self.product_model.check_and_create_alerts()

        # Reduce stock again below minimum
        self._set_product_stock(self.product_critical, 30.0)
        self.product_model.check_and_create_alerts()

        # Should have two alerts now - one resolved, one active
        all_alerts = self.alert_history_model.search(
            [("product_id", "=", self.product_critical.id)]
        )
        self.assertEqual(len(all_alerts), 2, "Should have two alerts total")

        active_alerts = all_alerts.filtered(lambda a: not a.resolved)
        resolved_alerts = all_alerts.filtered(lambda a: a.resolved)

        self.assertEqual(len(active_alerts), 1, "Should have one active alert")
        self.assertEqual(len(resolved_alerts), 1, "Should have one resolved alert")

    def test_mail_message_creation(self):
        """Test that mail messages are created for alerts"""
        # Clear any existing alerts and messages
        self.alert_history_model.search([]).unlink()

        # Get initial message count
        initial_message_count = self.env["mail.message"].search_count(
            [
                ("model", "=", "product.template"),
                ("res_id", "=", self.product_critical.id),
            ]
        )

        # Generate alert
        self.product_model.check_and_create_alerts()

        # Check that message was created
        final_message_count = self.env["mail.message"].search_count(
            [
                ("model", "=", "product.template"),
                ("res_id", "=", self.product_critical.id),
            ]
        )

        self.assertGreater(
            final_message_count,
            initial_message_count,
            "Mail message should be created for alert",
        )

        # Get the latest message
        message = self.env["mail.message"].search(
            [
                ("model", "=", "product.template"),
                ("res_id", "=", self.product_critical.id),
            ],
            order="id desc",
            limit=1,
        )

        self.assertIn(
            self.product_critical.name,
            message.body,
            "Message should contain product name",
        )
        self.assertIn(
            "Stock Alert", message.subject, "Message subject should mention stock alert"
        )

    def test_dashboard_grouping_by_category(self):
        """Test that dashboard can group products by category"""
        # This tests the search domain used by the dashboard
        dashboard_products = self.product_model.search(
            [("type", "=", "product"), ("minimum_stock", ">", 0)]
        )

        # Group by category manually (simulating what the view does)
        categories = dashboard_products.mapped("categ_id")

        self.assertIn(
            self.test_category,
            categories,
            "Test category should be in dashboard results",
        )

        # Products in test category
        category_products = dashboard_products.filtered(
            lambda p: p.categ_id == self.test_category
        )

        self.assertEqual(
            len(category_products),
            2,
            "Should have 2 products with minimum stock in test category",
        )
