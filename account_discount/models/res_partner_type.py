from odoo import fields, models


class ResPartnerType(models.Model):
    _name = "res.partner.type"

    name = fields.Char(string="Nombre", required=True)
    percentaje = fields.Float(string="Porcentaje", required=True)
