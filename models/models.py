from odoo import models, fields, api , exceptions, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_utils
import logging

_logger = logging.getLogger(__name__)

# Extensión del modelo de plantilla de producto para incluir relaciones con clientes y agentes.
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #Campo para guardar el valor arnian generado en la cotizacion. 
    x_val_arn = fields.Float(string='Valor Arnian',  store=True)
    # Campo para relacionar un producto con un cliente específico.
    related_partner_id = fields.Many2one('res.partner', string="Related Partner")
    # Campo para relacionar un producto con un agente específico.
    related_agent_id = fields.Many2one('res.users', string="Related Agent")
    
    is_quoted = fields.Boolean("Cotizado", default=False, help="Indica si el producto ha sido cotizado.")
    is_dedicated = fields.Boolean("Dedicado", default=False, help="Indica si el producto es dedicado.")
    current_quote = fields.Char('Current Quote', help="Cotizacion actual")
    output_number = fields.Char('Salida actual', help="Salida actual")

    is_in_carga = fields.Boolean("En Carga", default=False, help="Indica si el producto ya se asigno a una carga actualmente.")
    bee_notify = fields.Boolean("No Notificacion Beetrack", default=False, help="Indica si no se debe notificar el cliente, si esta en false, se notifica en true no se notifica")
    multi_quote = fields.Boolean("Extra", default=False, help="Campo extra")
    is_ready_for_bill = fields.Boolean("ReadyBill", default=False, help="Indica si el producto esta listo para cargarse a orden de entrega.")
    is_finished = fields.Boolean("Finalizada", default=False, help="Indica si el la entrada ya ha sido entregada \nNota: si una sola etiqueta se entrego entonces aun asi se marcara toda la entrada como finalizada.")
    reviewed = fields.Boolean("Revisada", default=False, help="Indica si el la entrada ya ha sido revisada por Arnian.")

    t_operacion = fields.Integer("Operacion", default=False, help="Indica el tipo de operacion de la mercancia.")

     # Nuevo campo tipo de pago
    tipo_pago = fields.Selection([
        ('contra_entrega', 'Contra Entrega'),
        ('transferencia', 'Transferencia'),
        ('patrocinio', 'Patrocinio'),
        ('cheque', 'Cheque'),
        ('tarjeta_de_credito', 'Tarjeta de credito'),
        ('estado_cuenta', 'Estado de Cuenta'),
        ('efectivo', 'Efectivo'),
    ], string="Tipo de Pago", help="Selecciona el tipo de pago del cliente")
    
    a_qty_etiquetas = fields.Integer("Etiquetas", default=False, help="Numero de etiquetas o bultos.")
    # Campo para almacenar la ubicación actual
    # Nota: el nombre del campo y su etiqueta se mantienen para compatibilidad
    # con la API existente.
    current_location = fields.Char('Current Location', help="Ubicacion actual")
    # Historial de cambios en el número de salida
    output_history_ids = fields.One2many('product.output.history', 'product_tmpl_id',
                                         string='Output History', readonly=True)
    
    def write(self, vals):
        if 'output_number' in vals:
            for record in self:
                if record.output_number and record.output_number != vals['output_number']:
                    self.env['product.output.history'].create({
                        'product_tmpl_id': record.id,
                        'output_number': record.output_number,
                    })
        result = super(ProductTemplate, self).write(vals)
        
        if 'reviewed' in vals and vals['reviewed']:
            for record in self:
                try:
                    if record.related_agent_id:
                        product_name = record.name.split('[')[0].strip() if record.name else 'Producto desconocido'
                        
                        # Crear una actividad para el usuario
                        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
                        self.env['mail.activity'].create({
                            'activity_type_id': activity_type_id,
                            'note': f"El producto '{product_name}' ha sido revisado.",
                            'user_id': record.related_agent_id.id,
                            'res_id': record.id,
                            'res_model_id': self.env['ir.model']._get('product.template').id,
                        })
                        
                        # Crear un mensaje en el chatter
                        self.env['mail.message'].sudo().create({
                            'model': 'product.template',
                            'res_id': record.id,
                            'message_type': 'notification',
                            'body': f"El producto '{product_name}' ha sido revisado.",
                            'partner_ids': [(4, record.related_agent_id.partner_id.id)],
                            'subject': f"Producto Revisado: {product_name}",
                        })
                        
                        _logger.info(f"Notificación y actividad creadas para el producto '{product_name}'")
                    else:
                        _logger.warning(f"No se ha asignado un agente para el producto '{record.name or 'Desconocido'}'")
                except Exception as e:
                    _logger.error(f"Error al crear notificación para el producto {record.id}: {str(e)}")
        
        return result

# Extensión del modelo de producto para heredar las relaciones de la plantilla de producto.
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Campos relacionados que heredan la información de la plantilla de producto correspondiente.
    related_partner_id = fields.Many2one('res.partner', string="Related Partner", related='product_tmpl_id.related_partner_id', readonly=True, store=True)
    related_agent_id = fields.Many2one('res.users', string="Related Agent", related='product_tmpl_id.related_agent_id', readonly=True, store=True)
    is_quoted = fields.Boolean(string="Cotizado", related='product_tmpl_id.is_quoted', readonly=True, store=False)
    is_dedicated = fields.Boolean(string="Dedicado", related='product_tmpl_id.is_dedicated', readonly=True, store=False)
    current_quote = fields.Char(string="Cotizacion actual", related='product_tmpl_id.current_quote', readonly=True, store=False)
    output_number = fields.Char(string="Salida actual", related='product_tmpl_id.output_number', readonly=True, store=False)
    bee_notify = fields.Boolean("No Notificacion Beetrack", related='product_tmpl_id.bee_notify', readonly=True, store=True)
    multi_quote = fields.Boolean("Extra", related='product_tmpl_id.multi_quote', readonly=True, store=True)
    is_ready_for_bill = fields.Boolean("ReadyBill", related='product_tmpl_id.is_ready_for_bill', readonly=True, store=True)
    is_finished = fields.Boolean("Finalizada", related='product_tmpl_id.is_finished', readonly=True, store=True)
    reviewed = fields.Boolean("Revisada", related='product_tmpl_id.reviewed', readonly=True, store=True)
    last_quoted_by = fields.Many2one('res.users', string="Last Quoted By", readonly=True, help="User who last quoted this product.")
    current_location = fields.Char('Current Location', help="Ubicacion actual", related='product_tmpl_id.current_location', readonly=True, store=True)
    is_in_carga = fields.Boolean("En Carga", default=False, help="Indica si el producto ya se asigno a una carga actualmente." ,related='product_tmpl_id.is_in_carga', readonly=True, store=True)
    t_operacion = fields.Integer("Operacion", default=False, help="Indica el tipo de operacion de la mercancia.", related='product_tmpl_id.t_operacion', readonly=True, store=True)


# Historial de salidas por producto
class ProductOutputHistory(models.Model):
    _name = 'product.output.history'
    _description = 'Historial de Salidas'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade')
    output_number = fields.Char('Output Number')
    changed_at = fields.Datetime('Changed At', default=fields.Datetime.now)


# Extensión del modelo de línea de pedido de venta para incluir funcionalidad adicional.
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Campo para almacenar un porcentaje de venta específico.
    x_percentage = fields.Float('Percentage', digits='Product Price', store=True)
    x_alias = fields.Char('Alias', store=True)
    x_customer_price = fields.Float('Customer Purchase Price', digits='Product Price', store=True)  
    # Método sobrescrito para crear líneas de pedido de venta.

    @api.model_create_multi
    def create(self, vals_list):
        # Antes de crear la línea, verifica si el producto ya ha sido cotizado.
        for vals in vals_list:
            vals['product_uom_qty'] = 1
            product_id = vals.get('product_id')
            if product_id:
                product = self.env['product.product'].browse(product_id)
                # Verifica que el tipo de producto no sea 'service'
                if product.detailed_type != 'service' and product.is_quoted:
                    raise exceptions.UserError(_('El producto seleccionado ya ha sido cotizado y no puede ser añadido a una nueva cotización.'))

                # Aplica un porcentaje predeterminado del cliente si no se proporcionó uno.
                if 'x_percentage' not in vals and 'order_id' in vals:
                    order = self.env['sale.order'].browse(vals['order_id'])
                    if order.partner_id.default_percentage:
                        vals['x_percentage'] = order.partner_id.default_percentage
                
                if product.product_tmpl_id.related_partner_id:
                    vals['x_alias'] = product.product_tmpl_id.related_partner_id.name

                 # Asegurar que x_customer_price es establecido correctamente.
                vals['x_customer_price'] = product.standard_price

        # Crear las líneas de pedido.
        lines = super(SaleOrderLine, self).create(vals_list)
        for line in lines:
            if line.product_id and line.product_id.type != 'service':  # Nuevamente, verifica que no sea un servicio
                # Comprueba si el producto asociado (template) ya ha sido cotizado
                if line.product_id.product_tmpl_id.is_quoted:
                    raise exceptions.UserError(_('El producto seleccionado ya ha sido cotizado y no puede ser añadido a una nueva cotización.'))

                # Marca el producto (template) como cotizado
                line.product_id.product_tmpl_id.current_quote = line.order_id.name
                line.product_id.product_tmpl_id.is_quoted = True
                line.product_id.product_tmpl_id.message_post(
                    body=_("Producto {} añadido a la cotización ({}) por {}.").format(line.product_id.display_name, line.order_id.name, self.env.user.name),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

            line.product_id.product_tmpl_id.x_val_arn = line.price_unit

            # Ajusta el precio unitario basado en el porcentaje y el precio estándar del producto.
            if line.x_percentage and line.product_id.standard_price:
                line.price_unit = (line.product_id.standard_price * line.x_percentage) / 100.0
        return lines

    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)

        if 'product_id' in vals or 'price_unit' in vals:
            for line in self:
                update_vals = {}
                if 'price_unit' in vals and line.product_id and line.product_id.type != 'service':
                    line.product_id.product_tmpl_id.write({'x_val_arn': vals['price_unit']})
                
                if 'product_id' in vals:
                    product = line.product_id
                    if product and product.product_tmpl_id and product.product_tmpl_id.related_partner_id:
                        update_vals['x_alias'] = product.product_tmpl_id.related_partner_id.name

                if line.product_id and line.product_id.type != 'service':
                    update_vals = {'x_customer_price': line.purchase_price}
                    
                # Aplicar los cambios acumulados a la línea de la orden.
                if update_vals:
                    line.write(update_vals)

        return result


    def unlink(self):
        try:
            for record in self:
                if record.order_id.state in ['draft', 'sent']:
                    product_tmpl = record.product_id.product_tmpl_id

                    # Desmarcar el producto como cotizado y vaciar el campo current_quote
                    product_tmpl.current_quote = ""
                    product_tmpl.is_quoted = False
                    product_tmpl.message_post(
                        body=_("Producto {} borrado de la cotización ({}) por {}.").format(record.product_id.display_name, record.order_id.name, self.env.user.name),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note'
                    )

            return super(SaleOrderLine, self).unlink()
        except Exception as e:
            raise exceptions.UserError(_("Ocurrió un error al eliminar la línea de cotización: %s") % str(e))



    # Métodos onchange para ajustar el precio unitario cuando cambia el producto, la cantidad o el porcentaje.
    @api.onchange('product_id', 'product_uom_qty', 'x_percentage')
    def _onchange_product_id_quantity_percentage(self):
        # Ajusta el precio unitario basado en el precio de lista del producto y el porcentaje predeterminado del cliente.
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            if self.order_id.partner_id.default_percentage and not self.x_percentage:
                self.x_percentage = self.order_id.partner_id.default_percentage
            if self.x_percentage and self.product_id.standard_price:
                self.price_unit = (self.product_id.standard_price * self.x_percentage) / 100.0
                
    @api.onchange('purchase_price', 'x_percentage')
    def _onchange_purchase_price(self):
        # Asegura que los campos necesarios están disponibles
        if self.purchase_price and self.x_percentage:
            # Calcula el nuevo precio unitario
            self.price_unit = (self.purchase_price * self.x_percentage) / 100
        elif self.purchase_price and not self.x_percentage:
            # Si no hay porcentaje, asume 100% (es decir, el precio unitario es igual al precio de compra)
            self.price_unit = self.purchase_price

   
      


    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_uom_qty(self):
        category_name = "Entrada"  # El nombre de la categoría deseada
        if self.product_id and self.product_id.categ_id.name == category_name and self.product_uom_qty != 1:
            self.product_uom_qty = 1
            return {
                'warning': {
                    'title': "Cantidad ajustada",
                    'message': "La cantidad para productos de la categoría 'Entrada' ha sido ajustada a 1.",
                }
            }
    
    def action_add_from_catalog(self):
        # Llamamos al super para obtener la acción original
        action = super(SaleOrderLine, self).action_add_from_catalog()
        
        # Verificamos si la acción tiene un contexto y luego agregamos o actualizamos el contexto con el filtro predeterminado
        if action.get('context'):
            # Es importante evaluar si el contexto es un string de diccionario y convertirlo a diccionario
            if isinstance(action['context'], str):
                action_context = safe_eval(action['context'])
            else:
                action_context = action['context']
            
            # Agregamos nuestro filtro personalizado al contexto
            action_context.update({'search_default_my_non_quoted_products': 1})
            action['context'] = action_context
        else:
            # Si no hay contexto, lo creamos
            action['context'] = {'search_default_my_non_quoted_products': 1}
        
        return action

# Extensión del modelo de cliente para incluir un porcentaje de venta predeterminado.
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo para almacenar un porcentaje de venta predeterminado para el cliente.
    default_percentage = fields.Float('Default Percentage', help="Default sales percentage for this customer.")
    # Campo para almacenar una coordenada predeterminada para el cliente.
    default_coordinates  = fields.Char('Coordinates ', help="Coordinates for this customer.")
