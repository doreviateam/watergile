from odoo import models, fields, api

class InterventionIntervention(models.Model):
    _name = 'intervention.intervention'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)    
    active = fields.Boolean(default=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', tracking=True)
    
    project_id = fields.Many2one('project.project', string='Projet', required=True,
                                domain="[('is_watergile', '=', True)]", tracking=True)
    client_id = fields.Many2one(related='project_id.partner_id', string='Client', store=True)
    client_logo = fields.Binary(related='client_id.image_1920', string="Logo client", readonly=True)    
    date_start = fields.Date(string='Date de début', required=True, default=fields.Date.context_today, tracking=True)
    date = fields.Date(string='Date de fin', required=True, tracking=True)
    inter_type = fields.Selection(selection=[
        ('orderd_prepaid', 'Forfait'),
        ('delivered_timesheet', 'Régie'),
        ('delivered_milestones', 'Jalons'),
        ('delivered_manual', 'Quantités livrées'),
    ], string='Service', default=False, required=True, tracking=True)
    
    sequence = fields.Char(string='Numéro', readonly=True, copy=False)
    inter_product_name = fields.Char(
        string='Produit',
        compute='_compute_inter_product_name',
        store=True
    )
    inter_product_id = fields.Many2one(comodel_name='product.template', readonly=True, copy=False,
                                    context={'active_test': False})
    inter_uom_id = fields.Many2one(comodel_name='uom.uom', string='Unité de mesure', required=True,
                             domain=[('category_id.name', 'in', ['Temps de travail', 'Unité']), 
                                   ('name', 'in', ['Heures', 'Unité(s)', 'Jours'])],
                             default=lambda self: self.env.ref('uom.product_uom_day'),
                             tracking=True)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Devise', required=True,
                                  default=lambda self: self.env.company.currency_id)
    inter_price = fields.Monetary(string='Montant', help='Montant total de l\'intervention', tracking=True)
    inter_unit_price = fields.Monetary(string='Prix unitaire', compute='_compute_inter_unit_price')
    inter_qty = fields.Float(string='Quantité', default=1, tracking=True)


    @api.depends('name', 'project_id.name', 'inter_type')
    def _compute_inter_product_name(self):
        for record in self:
            type_map = {
                'orderd_prepaid': 'Forfait',
                'delivered_timesheet': 'Régie',
                'delivered_milestones': 'Jalons',
                'delivered_manual': 'Quantités livrées',
            }
            if record.name and record.project_id:
                type_name = type_map.get(record.inter_type, 'Inter')
                record.inter_product_name = f"{type_name} - {record.project_id.name} - {record.name}"
            else:
                record.inter_product_name = False

    @api.depends('inter_price', 'inter_qty')
    def _compute_inter_unit_price(self):
        for record in self:
            record.inter_unit_price = record.inter_price / record.inter_qty if record.inter_qty > 0 else 0

    def _get_service_type(self):
        """Mapping entre types d'intervention et types de service"""
        mapping = {
            'orderd_prepaid': 'timesheet',
            'delivered_timesheet': 'timesheet',
            'delivered_milestones': 'manual',
            'delivered_manual': 'manual',
        }
        return mapping.get(self.inter_type, 'manual')

    @api.model_create_multi 
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            sequence = self.env['ir.sequence'].next_by_code('intervention.product.sequence')
            record.sequence = sequence
            
            product = self.env['product.template'].create({
                'name': record.inter_product_name,
                'image_1920': record.client_logo,
                'active': False,
                'sale_ok': True,
                'purchase_ok': False,
                'type': 'service',
                'detailed_type': 'service',
                'default_code': f"INTER-{sequence}",
                'service_tracking': 'no',
                'service_type': 'manual',
                'expense_policy': 'no',
                'uom_id': record.inter_uom_id.id,
                'uom_po_id': record.inter_uom_id.id,
                'list_price': record.inter_unit_price,
            })
            record.inter_product_id = product
       
        return records

    @api.onchange('project_id', 'name', 'inter_type', 'inter_price', 'inter_qty')
    def _onchange_intervention_fields(self):
        if self.inter_qty <= 0:
            return {
                'warning': {
                    'title': 'Attention',
                    'message': 'La quantité doit être supérieure à 0'
                }
            }
        if self.inter_price < 0:
            return {
                'warning': {
                    'title': 'Attention',
                    'message': 'Le montant ne peut pas être négatif'
                }
            }

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            product_vals = {}
            
            # Mise à jour du nom si nécessaire
            if 'name' in vals or 'project_id' in vals:
                product_vals['name'] = record.inter_product_name

            # Mise à jour du prix si nécessaire
            if 'inter_unit_price' in vals:
                product_vals['list_price'] = record.inter_unit_price

            # Mise à jour de l'unité de mesure si nécessaire
            if 'inter_uom_id' in vals:
                product_vals['uom_id'] = record.inter_uom_id.id

            # Si des modifications sont nécessaires, mettre à jour le produit
            if product_vals and record.inter_product_id:
                record.inter_product_id.write(product_vals)

        return result

