from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_mp_ajax_boy_countries_state(self):
        states = self.env['res.country.state'].sudo().search([])
        countries2 = []
        for state in states:
            if state.country_id.id == 221:
                countries2.append(state)
        return countries2