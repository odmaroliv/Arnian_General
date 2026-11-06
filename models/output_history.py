from odoo import models, fields

class ProductOutputHistory(models.Model):
    _name = 'product.output.history'
    _description = 'Historial de Salidas de Producto'

    product_id = fields.Many2one('product.template', string='Producto', required=True)
    previous_output = fields.Char(string='Salida Anterior')
    new_output = fields.Char(string='Nueva Salida')
    changed_by = fields.Many2one('res.users', string='Modificado por', default=lambda self: self.env.user)
    changed_at = fields.Datetime(string='Fecha de Cambio', default=fields.Datetime.now)
