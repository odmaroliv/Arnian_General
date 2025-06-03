from odoo.tests.common import TransactionCase
from odoo import exceptions

class TestSaleOrderLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.product_tmpl = self.env['product.template'].create({
            'name': 'Test Product',
            'detailed_type': 'product',
            'list_price': 10.0,
            'standard_price': 5.0,
            'is_quoted': True,
        })
        self.product = self.product_tmpl.product_variant_id
        self.sale_order = self.env['sale.order'].create({'partner_id': self.partner.id})

    def test_create_line_with_quoted_product_raises(self):
        with self.assertRaises(exceptions.UserError):
            self.env['sale.order.line'].create({
                'order_id': self.sale_order.id,
                'product_id': self.product.id,
            })

