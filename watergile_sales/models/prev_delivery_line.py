from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PrevDeliveryLine(models.Model):
    _name = 'prev.delivery.order.line'
    _description = 'Ligne de prév-livraison'
    _order = 'date_delivery, id'

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    sequence = fields.Integer(string='Sequence', default=10)
    prev_delivery_id = fields.Many2one(comodel_name='prev.delivery.order', string='Prév-Livraison', required=True, ondelete='cascade',
                                       help='La prévision de livraison liée à la ligne')
    
    partner_delivery_id = fields.Many2one(comodel_name='res.partner', string='Client destinataire',domain="[('type', '=', 'contact')]",
                                          help='Le partenaire destinataire')

    delivery_address_id = fields.Many2one(comodel_name='res.partner', string='Adresse de livraison', 
                                          domain="[('type', '=', 'delivery'), ('parent_id', '=', partner_delivery_id)]",
                                          help="L'adresse de livraison sélectionnée")

    product_id = fields.Many2one(comodel_name='product.product', string='Produit',  domain="[]", help='Le produit à livrer')
    
    quantity = fields.Float(
        string='Quantité', 
        required=True, 
        default=1.0, 
        help='La quantité liée à la ligne'
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Devise', 
        related='prev_delivery_id.currency_id', 
        store=True, 
        readonly=True,
        help='La devise liée à la ligne'
    )
    
    unit_price = fields.Monetary(
        string='Prix unitaire', 
        currency_field='currency_id', 
        help='Le prix unitaire'
    )
    
    total_price = fields.Monetary(
        string='Prix total', 
        currency_field='currency_id', 
        compute='_compute_total_price', 
        store=True,
        help='Le prix total'
    )
    
    date_delivery = fields.Date(
        string='Date de livraison', 
        required=True, 
        default=fields.Date.context_today,
        help='La date de livraison prévue'
    )
    
    state = fields.Selection(
        related='prev_delivery_id.state', 
        string='État', 
        store=True
    )
    
    company_id = fields.Many2one(
        related='prev_delivery_id.company_id', 
        store=True, 
        string='Société'
    )

    @api.depends('quantity', 'unit_price', 'currency_id')
    def _compute_total_price(self):
        for line in self:
            if line.currency_id:
                line.total_price = line.currency_id.round(line.quantity * line.unit_price)
            else:
                line.total_price = line.quantity * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price

    @api.onchange('partner_delivery_id')
    def _onchange_partner_delivery_id(self):
        self.delivery_address_id = False
        if not self.partner_delivery_id:
            return

        delivery_addresses = self.env['res.partner'].search([
            ('parent_id', '=', self.partner_delivery_id.id),
            ('type', '=', 'delivery')
        ])

        if not delivery_addresses:
            return {
                'warning': {
                    'title': _('Aucune adresse de livraison'),
                    'message': _('Ce client n\'a pas d\'adresse de livraison configurée.')
                }
            }

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('La quantité doit être supérieure à 0.'))

    @api.constrains('delivery_address_id')
    def _check_delivery_address(self):
        for line in self:
            if line.partner_delivery_id and not line.delivery_address_id:
                raise ValidationError(_('Une adresse de livraison doit être sélectionnée.'))



