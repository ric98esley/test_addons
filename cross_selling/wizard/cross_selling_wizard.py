from odoo import api, fields, models


class CrossSellingWizard(models.TransientModel):
    _name = "cross.selling.wizard"
    _description = "Cross Selling Wizard"

    sale_order_id = fields.Many2one("sale.order", required=True)
    line_ids = fields.One2many(
        "cross.selling.wizard.line", "wizard_id", string="Suggestions"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(CrossSellingWizard, self).default_get(fields_list)
        if self.env.context.get("active_id"):
            order = self.env["sale.order"].browse(self.env.context.get("active_id"))
            res["sale_order_id"] = order.id

            lines = []
            order_product_ids = order.order_line.mapped("product_id").ids
            rules = self.env["product.cross.sell"].search(
                [("product_id", "in", order_product_ids)]
            )

            set(order_product_ids)

            for rule in rules:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": rule.suggested_product_id.id,
                            "quantity": 1.0,
                            "is_selected": True,
                        },
                    )
                )

            res["line_ids"] = lines
        return res

    def action_add_suggestions(self):
        self.ensure_one()
        order = self.sale_order_id
        for line in self.line_ids:
            if line.is_selected:
                order.order_line = [
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.quantity,
                        },
                    )
                ]
        return {"type": "ir.actions.act_window_close"}


class CrossSellingWizardLine(models.TransientModel):
    _name = "cross.selling.wizard.line"
    _description = "Cross Selling Wizard Line"

    wizard_id = fields.Many2one("cross.selling.wizard")
    product_id = fields.Many2one("product.product", required=True, readonly=True)
    quantity = fields.Float(default=1.0)
    is_selected = fields.Boolean(default=True)
