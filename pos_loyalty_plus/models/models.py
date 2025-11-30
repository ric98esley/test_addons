# from odoo import models, fields, api


# class po_loyalty_plus(models.Model):
#     _name = 'po_loyalty_plus.po_loyalty_plus'
#     _description = 'po_loyalty_plus.po_loyalty_plus'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
