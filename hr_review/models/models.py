# from odoo import models, fields, api


# class hr_review(models.Model):
#     _name = 'hr_review.hr_review'
#     _description = 'hr_review.hr_review'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
