from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2one("res.partner.type")
