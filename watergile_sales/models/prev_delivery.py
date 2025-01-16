from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PrevDelivery(models.Model):
    _name = 'prev.delivery.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prévision de livraison'
    _order = 'date_order desc, id desc'

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, 
                      default=lambda self: _('New'))
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True,
        domain="[('type', '=', 'contact')]",
        tracking=True,
        help='Le client principal'
    )
    
    partner_mandant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Mandant',
        domain="[('type', '=', 'contact')]",
        tracking=True,
        help='Le mandant éventuel'
    )
    
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string='Facturation',
        domain="[('type', '=', 'invoice'), ('parent_id', '=', partner_id)]",
        tracking=True,
        help='L\'adresse de facturation'
    )
    
    date_order = fields.Date(
        string='Date de commande',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Commercial',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    note = fields.Text(string='Notes')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('sale', 'Commande créée'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', required=True, tracking=True)
    
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Commande de vente',
        copy=False,
        readonly=True
    )
    
    delivery_count = fields.Integer(
        string='Nombre de livraisons',
        compute='_compute_delivery_count'
    )
    
    line_ids = fields.One2many(
        comodel_name='prev.delivery.order.line',
        inverse_name='prev_delivery_id',
        string='Lignes',
        copy=True
    )
    
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('prev.delivery.order') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.total_price')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('total_price'))

    def _compute_delivery_count(self):
        for order in self:
            order.delivery_count = len(order.sale_id.picking_ids) if order.sale_id else 0

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commande de vente'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_id.id,
            'target': 'current',
        }

    def action_view_deliveries(self):
        self.ensure_one()
        if not self.sale_id:
            return
        
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Livraisons'),
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_id.picking_ids.ids)],
            'context': {'create': False},
            'target': 'current',
        }
        
        if len(self.sale_id.picking_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_id.picking_ids.id
            })
        return action

    def action_toggle_fullscreen(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'toggle_form_fullscreen',
            'target': 'current',
            'params': {
                'model': self._name,
                'id': self.id
            }
        }


