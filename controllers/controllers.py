from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ReportByDate(http.Controller):
    @http.route('/report_by_date', type='http', auth='user', website=True)
    def report_by_date(self, **kwargs):
        return request.render('Arnian_General.report_by_date_template')

    @http.route('/report_by_date/submit', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def report_by_date_submit(self, **kwargs):
        date_selected = kwargs.get('date')
        user = request.env.user
        partner = user.partner_id
        main_partner_id = partner.parent_id.id if partner.parent_id else partner.id

        _logger.info(f"Received data - Date selected: {date_selected}, User: {user.name}, Main Partner ID: {main_partner_id}")

        SaleOrder = request.env['sale.order']
        orders = SaleOrder.search([
            ('partner_id', 'in', [main_partner_id]),
            ('date_order', '>=', date_selected),
            ('date_order', '<=', fields.Date.today())
        ])
        
       # _logger.info(f"Found {len(orders)} orders for the main partner as of today")

        products_data = []
        for order in orders:
            for line in order.order_line:
                products_data.append({
                    'name': line.name,  
                    #'description': line.name,  
                    'x_alias': line.x_alias,
                    'x_percentage': line.x_percentage,
                    'x_customer_price': line.x_customer_price,
                    'unit_price': line.price_unit,
                })

      #  _logger.info(f"Collected {len(products_data)} product lines from the orders")

        return request.render('Arnian_General.report_by_date_result', {
            'products': products_data,
            'date_selected': date_selected
        })
