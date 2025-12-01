from odoo import api, fields, models


class ProductCrossSell(models.Model):
    _name = "product.cross.sell"
    _description = "Cross Selling Product Relation"
    _rec_name = "src_id"

    src_id = fields.Many2one(
        "product.template",
        string="Main Product",
        required=True,
        ondelete="cascade",
        index=True,
    )
    dest_id = fields.Many2one(
        "product.template",
        string="Optional Product",
        required=True,
        ondelete="cascade",
        index=True,
    )

    _sql_constraints = [
        (
            "unique_product_relation",
            "unique(src_id, dest_id)",
            "This cross-selling relation already exists!",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to sync with optional_product_ids"""
        records = super().create(vals_list)
        # Sync with optional_product_ids (skip reverse sync to avoid loops)
        if not self.env.context.get("skip_cross_sell_sync"):
            for record in records:
                if record.src_id and record.dest_id:
                    record.src_id.with_context(skip_cross_sell_sync=True).write(
                        {"optional_product_ids": [(4, record.dest_id.id)]}
                    )
        return records

    def write(self, vals):
        """Override write to sync with optional_product_ids"""
        if not self.env.context.get("skip_cross_sell_sync"):
            # Remove old relations
            for record in self:
                if record.src_id and record.dest_id:
                    record.src_id.with_context(skip_cross_sell_sync=True).write(
                        {"optional_product_ids": [(3, record.dest_id.id)]}
                    )

        result = super().write(vals)

        if not self.env.context.get("skip_cross_sell_sync"):
            # Add new relations
            for record in self:
                if record.src_id and record.dest_id:
                    record.src_id.with_context(skip_cross_sell_sync=True).write(
                        {"optional_product_ids": [(4, record.dest_id.id)]}
                    )

        return result

    def unlink(self):
        """Override unlink to sync with optional_product_ids"""
        # Remove relations before unlinking
        if not self.env.context.get("skip_cross_sell_sync"):
            for record in self:
                if record.src_id and record.dest_id:
                    record.src_id.with_context(skip_cross_sell_sync=True).write(
                        {"optional_product_ids": [(3, record.dest_id.id)]}
                    )
        return super().unlink()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        """Override write to sync optional_product_ids with product.cross.sell"""
        result = super().write(vals)

        if "optional_product_ids" in vals:
            # For each product template
            for product in self:
                # Get current optional_product_ids after the write
                current_optional_ids = set(product.optional_product_ids.ids)

                # Get existing cross-sell records for this product
                existing_records = self.env["product.cross.sell"].search(
                    [("src_id", "=", product.id)]
                )
                existing_dest_ids = set(existing_records.mapped("dest_id").ids)

                # Find products to add (in current but not in existing)
                to_add = current_optional_ids - existing_dest_ids

                # Find products to remove (in existing but not in current)
                to_remove = existing_dest_ids - current_optional_ids

                # Create new cross-sell records (skip sync to avoid loops)
                for dest_id in to_add:
                    self.env["product.cross.sell"].with_context(
                        skip_cross_sell_sync=True
                    ).create(
                        {
                            "src_id": product.id,
                            "dest_id": dest_id,
                        }
                    )

                # Delete removed cross-sell records (skip sync to avoid loops)
                if to_remove:
                    records_to_delete = existing_records.filtered(
                        lambda r: r.dest_id.id in to_remove
                    )
                    records_to_delete.with_context(skip_cross_sell_sync=True).unlink()

        return result
