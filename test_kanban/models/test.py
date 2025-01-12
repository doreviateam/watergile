from odoo import models, fields

class TestKanban(models.Model):
    _name = 'test.kanban'
    _description = 'Test Kanban'

    name = fields.Char(string='Nom', required=True)
    partner_id = fields.Many2one('res.partner', string='Client')
