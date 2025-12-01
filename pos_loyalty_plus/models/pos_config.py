from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    loyalty_points_per_currency = fields.Float(
        string="Points per Currency Unit",
        help="How many loyalty points are given per currency unit spent.",
        default=0.0,
    )

    loyalty_program_id = fields.Many2one(
        "loyalty.program",
        string="Loyalty Program",
        help="The loyalty program associated with this POS configuration.",
    )

    @api.model
    def create(self, vals):
        res = super(PosConfig, self).create(vals)
        if vals.get("loyalty_points_per_currency"):
            res._update_loyalty_program()
        return res

    def write(self, vals):
        res = super(PosConfig, self).write(vals)
        if "loyalty_points_per_currency" in vals:
            self._update_loyalty_program()
        return res

    def _update_loyalty_program(self):
        for config in self:
            if config.loyalty_points_per_currency > 0:
                if not config.loyalty_program_id:
                    # Create a new loyalty program if one doesn't exist
                    program = self.env["loyalty.program"].create(
                        {
                            "name": f"Loyalty Program - {config.name}",
                            "program_type": "loyalty",
                            "applies_on": "both",
                            "trigger": "auto",
                            "portal_visible": True,
                            "pos_config_ids": [(4, config.id)],
                        }
                    )
                    config.loyalty_program_id = program.id

                # Update or create the rule for points accumulation
                program = config.loyalty_program_id

                # Check if a rule exists
                rule = program.rule_ids.filtered(
                    lambda r: r.reward_point_mode == "money"
                )
                if rule:
                    rule.write(
                        {"reward_point_amount": config.loyalty_points_per_currency}
                    )
                else:
                    self.env["loyalty.rule"].create(
                        {
                            "program_id": program.id,
                            "reward_point_mode": "money",
                            "reward_point_amount": config.loyalty_points_per_currency,
                        }
                    )
