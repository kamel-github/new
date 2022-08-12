

from odoo import models,fields,api, _

class InheritResPartnerdelivery(models.Model):
    _inherit = "res.partner"


    boydeliveryform = fields.Boolean(string="boydeliveryform", store=True, default=False)
    is_delivery_boy = fields.Boolean(string="Is a Delivery Boy", copy=False)
    description = fields.Char(string='Description', store=True)

