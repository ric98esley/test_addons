from odoo import _, fields, models
from odoo.exceptions import UserError


class LoyaltyReportWizard(models.TransientModel):
    _name = "pos.loyalty.report.wizard"
    _description = "Loyalty History Report Wizard"

    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True, default=fields.Date.context_today)

    def action_print_report(self):
        self.ensure_one()
        if self.start_date > self.end_date:
            raise UserError(_("Start date cannot be later than end date."))

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
            },
        }
        # This calls the report action we will define in XML
        return self.env.ref(
            "pos_loyalty_plus.action_report_loyalty_period"
        ).report_action(self, data=data)
