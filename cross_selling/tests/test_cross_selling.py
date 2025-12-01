from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install", "cross_selling")
class TestCrossSelling(TransactionCase):
    def setUp(self):
        super(TestCrossSelling, self).setUp()
        self.product_a = self.env["product.product"].create({"name": "Product A"})
        self.product_b = self.env["product.product"].create({"name": "Product B"})
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def test_cross_selling_relation(self):
        """Test that creating a product.cross.sell record updates the optional_product_ids"""
        # Create Cross Selling Rule: A -> B using the new model
        self.env["product.cross.sell"].create(
            {
                "src_id": self.product_a.product_tmpl_id.id,
                "dest_id": self.product_b.product_tmpl_id.id,
            }
        )

        # Verify that Product B is now an optional product of Product A
        self.assertIn(
            self.product_b.product_tmpl_id,
            self.product_a.product_tmpl_id.optional_product_ids,
            "Product B should be in optional_product_ids of Product A",
        )

    def test_cross_selling_reverse(self):
        """Test that adding to optional_product_ids creates a product.cross.sell record"""
        # Add Product A as optional to Product B
        self.product_b.product_tmpl_id.optional_product_ids = [
            (4, self.product_a.product_tmpl_id.id)
        ]

        # Check if the relation record exists
        relation = self.env["product.cross.sell"].search(
            [
                ("src_id", "=", self.product_b.product_tmpl_id.id),
                ("dest_id", "=", self.product_a.product_tmpl_id.id),
            ]
        )
        self.assertTrue(relation, "Relation record should exist")
