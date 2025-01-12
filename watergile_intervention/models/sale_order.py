from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    intervention_domain_id = fields.Many2one(comodel_name='intervention.intervention', string='Intervention')
    
