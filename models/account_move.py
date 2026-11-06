from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Relación real (no texto) con las cotizaciones/órdenes de venta de la factura.
    # Se guarda en BD para poder usarla en la lista, filtros, agrupaciones y exportación.
    arnian_sale_order_ids = fields.Many2many(
        'sale.order',
        'account_move_arnian_sale_order_rel',
        'move_id',
        'order_id',
        string='Cotizaciones',
        compute='_compute_arnian_sale_order_ids',
        store=True,
        copy=False,
        help="Cotizaciones / órdenes de venta ligadas a las líneas de esta factura.",
    )

    @api.depends('line_ids.sale_line_ids')
    def _compute_arnian_sale_order_ids(self):
        for move in self:
            move.arnian_sale_order_ids = move.line_ids.sale_line_ids.order_id
