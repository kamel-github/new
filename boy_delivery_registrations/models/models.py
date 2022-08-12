# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class boy_delivery_registrations(models.Model):
#     _name = 'boy_delivery_registrations.boy_delivery_registrations'
#     _description = 'boy_delivery_registrations.boy_delivery_registrations'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
