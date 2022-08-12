# -*- coding: utf-8 -*-
# from odoo import http


# class BoyDeliveryRegistrations(http.Controller):
#     @http.route('/boy_delivery_registrations/boy_delivery_registrations', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/boy_delivery_registrations/boy_delivery_registrations/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('boy_delivery_registrations.listing', {
#             'root': '/boy_delivery_registrations/boy_delivery_registrations',
#             'objects': http.request.env['boy_delivery_registrations.boy_delivery_registrations'].search([]),
#         })

#     @http.route('/boy_delivery_registrations/boy_delivery_registrations/objects/<model("boy_delivery_registrations.boy_delivery_registrations"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('boy_delivery_registrations.object', {
#             'object': obj
#         })


import werkzeug
import odoo



from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import TableCompute, QueryURL, WebsiteSale

from odoo.addons.portal.controllers.web import Home
from odoo.addons.website.controllers.main import Website
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import logging



_logger = logging.getLogger(__name__)
import urllib.parse as urlparse

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

SPG = 20  # Shops/sellers Per Page
SPR = 4   # Shops/sellers Per Row

class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        if request.session.uid:
            current_user = request.env['res.users'].sudo().browse(request.session.uid)
            if not current_user.has_group('base.group_user') and current_user.has_group(
                    'odoo_marketplace.marketplace_draft_seller_group') and current_user.partner_id.seller:
                request.uid = request.session.uid
                try:
                    context = request.env['ir.http'].webclient_rendering_context()
                    response = request.render('web.webclient_bootstrap', qcontext=context)
                    response.headers['X-Frame-Options'] = 'DENY'
                    return response
                except AccessError:
                    return werkzeug.utils.redirect('/web/login?error=access')
        return super(Home, self).web_client(s_action, **kw)


class AuthSignupHome(Website):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        ensure_db()
        response = super(AuthSignupHome, self).web_login(redirect=redirect, *args, **kw)
        # if request.params['login_success']:
            # current_user = request.env['res.users'].browse(request.uid)
            # if not current_user.has_group('base.group_user') and current_user.has_group(
            #         'odoo_marketplace.marketplace_draft_seller_group') and current_user.partner_id.seller:
            #     seller_dashboard_menu_id = \
            #     request.env['ir.model.data'].check_object_reference('odoo_marketplace', 'wk_seller_dashboard')[1]
            #     redirect = "/web#menu_id=" + str(seller_dashboard_menu_id)
            #     return http.redirect_with_hash(redirect)
        return response

    def _signup_with_values(self, token, values):
        params = dict(request.params)
        # is_seller = params.get('is_seller')
        country_id = params.get('country_id')
        state_id = params.get('state_id')
        is_delivery_boy = params.get('is_delivery_boy')
        # if is_seller and is_seller == 'on':
        #     values.update({
        #         'is_seller': True,
        #         'country_id': int(country_id) if country_id else country_id,
        #         'url_handler': params.get('url_handler'),
        #     })

        if is_delivery_boy and is_delivery_boy == 'on':
            values.update({
                'boydeliveryform': True,
                'active': False,
                'is_delivery_boy': True,
                'country_id': int(country_id) if country_id else country_id,
                'state_id': int(state_id) if state_id else state_id,
                'description': params.get('mp_description'),
            })
        return super(AuthSignupHome, self)._signup_with_values(token, values)

        # Boy Delivery Sign up

    @http.route('/boydelivery/signup', type='http', auth="public", website=True)
    def boy_delivery_signup_form(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if True:
            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    self.do_signup(qcontext)
                    self.web_login(*args, **kw)
                    return request.render('boy_delivery_registrations.wk_mp_thanks_page', {})
                except UserError as e:
                    qcontext['error'] = e.name or e.value
                except (SignupError, AssertionError) as e:
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        qcontext["error"] = _("Another user is already registered using this email address.")
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")
        return request.render('boy_delivery_registrations.wk_mp_boy_landing_page', qcontext)


class MarketplaceboyProfile(http.Controller):

     @http.route(['/boy/profile/<int:boy_id>',
                     '/boy/profile/<int:boy_id>/page/<int:page>',
                     '/boy/profile/<boy_url_handler>',
                     '/boy/profile/<boy_url_handler>/page/<int:page>'],
                    type='http', auth="public", website=True)
     def boy(self, boy_id=None, boy_url_handler=None, page=0, category=None, search='', ppg=False, **post):
         boy = url = False
         uid, context, env = request.uid, dict(request.env.context), request.env
         # if boy_url_handler:
         #     boy = request.env["res.partner"].sudo().search([("url_handler", "=", str(boy_url_handler))], limit=1)
         #     url = "/boy/profile/" + str(boy.url_handler)
         if boy_id:
             boy = env['res.partner'].sudo().browse(boy_id)
             wk_name = boy.sudo().name.strip().replace(" ", "-")
             url = '/boy/profile/' + wk_name + '-' + str(boy.id)
         if not boy:
             return request.render("http_routing.403")

         # if boy and not boy.active:
         #     officer_group = env.ref('odoo_marketplace.marketplace_officer_group')
         #     manager_group = env.ref('odoo_marketplace.marketplace_manager_group')
         #     user_obj = env.user
         #     group_bool_val = [i in user_obj.groups_id.ids for i in (officer_group.id, manager_group.id)]
         #     group_exist = True in group_bool_val
         #     if not group_exist and user_obj.url_handler != boy.url_handler:
         #         return request.render("http_routing.403")
         # if not ppg:
         #     ppg = request.env['website'].get_current_website().shop_ppg
         #
         # PPR = request.env['website'].get_current_website().shop_ppr
         # if ppg:
         #     try:
         #         ppg = int(ppg)
         #     except ValueError:
         #         ppg = PPG
         #     post["ppg"] = ppg
         # else:
         #     ppg = PPG

         values = {
             'boy': boy,
             # 'search': search,
             # 'rows': PPR,
             # 'bins': TableCompute().process(products, ppg, PPR),
             # 'ppg': ppg,
             # 'ppr': PPR,
             # 'pager': pager,
             # 'products': products,
             # "keep": keep,
             # 'compute_currency': compute_currency,
             # "pricelist": pricelist,
             # "sales_count": sales_count,
             # "already_recommend": recommend_id.recommend_state if recommend_id else None,
             # "product_count": int(product_count),
         }
         return request.render("boy_delivery_registrations.mp_boy_profile", values)

     def _get_boy_search_domain(self, search):
         domain = [("active", "=", True), ("is_delivery_boy", '=', True)]
         if search:
             for srch in search.split(" "):
                 domain += [('name', 'ilike', srch)]
         return domain

     @http.route([
         '/boydelivery/list/'
     ], type='http', auth="public", website=True)
     def load_mp_all_deliveryboy(self, page=0, search='', ppg=False, **post):
         if not ppg:
             ppg = request.env['website'].get_current_website().shop_ppg

         PPR = request.env['website'].get_current_website().shop_ppr

         if ppg:
             try:
                 ppg = int(ppg)
             except ValueError:
                 ppg = SPG
             post["ppg"] = ppg
         else:
             ppg = SPG

         domain = self._get_boy_search_domain(search)
         keep = QueryURL('/boydelivery/list', search=search)

         url = "/boydelivery/list"
         if search:
             post["search"] = search

         boy_obj = request.env['res.partner']
         boy_count = boy_obj.sudo().search_count(domain)
         total_active_boy = boy_obj.sudo().search_count(self._get_boy_search_domain(""))
         pager = request.website.pager(url=url, total=boy_count, page=page, step=ppg, scope=7, url_args=post)
         boy_objs = boy_obj.sudo().search(domain, limit=ppg, offset=pager['offset'])

         values = {
             'search': search,
             'pager': pager,
             'boy_objs': boy_objs,
             'search_count': boy_count,  # common for all searchbox
             'bins': TableCompute().process(boy_objs, ppg, PPR),
             'ppg': ppg,
             'ppr': PPR,
             'rows': SPR,
             'keep': keep,
             'total_active_boy': total_active_boy,
         }
         return request.render("boy_delivery_registrations.boys_list", values)


#