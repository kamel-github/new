#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import models,fields,api, _

class InheritResUsers(models.Model):
    _inherit = "res.users"

    is_delivery_boy = fields.Boolean(string="Is a Delivery Boy", copy=False, related='partner_id.is_delivery_boy')
    # boydeliveryform = fields.Boolean(string="boydeliveryform", related='partner_id.boydeliveryform')
    # description = fields.Char(string='Description', related='partner_id.description')

    @api.model
    def signup(self, values, token=None):
        """ """
        context = dict(self._context)
        is_delivery_boy = values.get('is_delivery_boy')
        if is_delivery_boy:
            context["is_delivery_boy"] = is_delivery_boy
            values.pop("is_delivery_boy")
        return super(InheritResUsers, self.with_context(context)).signup(values, token)


    # @api.multi
    def toggle_is_delivery_boy(self):
        for user in self:
            if self.is_delivery_boy:
                self.partner_id.is_delivery_boy = False
            else:
                self.partner_id.is_delivery_boy = True
