from odoo import models, fields

class ProductCargaHistory(models.Model):
    _name = 'product.carga.history'
    _description = 'Historial de Cargas de Producto'

    product_id = fields.Many2one('product.template', string='Producto', required=True)
    previous_carga = fields.Char(string='Carga Anterior')
    new_carga = fields.Char(string='Nueva Carga')
    changed_by = fields.Many2one('res.users', string='Modificado por', default=lambda self: self.env.user)
    changed_at = fields.Datetime(string='Fecha de Cambio', default=fields.Datetime.now)
