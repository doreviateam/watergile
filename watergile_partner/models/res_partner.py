from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(
        selection_add=[
            ('contact', 'Contact'),
            ('invoice', 'Invoice Address'),
            ('delivery', 'Delivery Address'),
            ('other', 'Other Address'),
            ('private', 'Private Address'),
        ],
        ondelete={
            'contact': 'set default',
            'invoice': 'set default',
            'delivery': 'set default',
            'other': 'set default',
            'private': 'set default',
        }
    )

    hierarchy_relation = fields.Selection([
        ('other', 'Autre'),
        ('agency', 'Agence'),
        ('headquarters', 'Siège')
    ], string='Établissement', 
       default='other',
       help="Définit le type d'établissement dans la structure organisationnelle")

    company_badge_display = fields.Char(
        string='Badge',
        compute='_compute_company_badge_display',
        store=True,
        help="Badge de l'entité"
    )

    badge_color = fields.Char(
        string='Couleur du badge',
        compute='_compute_company_badge_display',
        store=True
    )

    relation_description = fields.Char(string="Description de la relation", help="Description complémentaire de la relation")     
    region_id = fields.Many2one(comodel_name='res.region',  string='Région', ondelete='restrict', index=True, help="Région de l'entité")
    partner_blaz_id = fields.Many2one(comodel_name='partner.blaz', string='Blaz', help='Blaz associé à ce partenaire')
    
    
    # Champs de base pour la localisation
    department_id = fields.Many2one(
        'res.country.department',
        string='Département',
        domain="[('country_id.code', '=', 'FR')]"
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='Région',
        related='department_id.state_id',
        store=True,
        readonly=True
    )



    @api.model
    def _valid_field_parameter(self, field, name):
        """Permet de définir les paramètres des champs"""
        return name in ['widget', 'options'] or super()._valid_field_parameter(field, name)

    

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Permet de définir les paramètres des champs"""
        if self.department_id:
            self.country_id = self.department_id.country_id
            self.state_id = self.department_id.state_id

    @api.onchange('zip', 'country_id')
    def _onchange_zip_country(self):
        """Permet de définir les paramètres des champs"""
        if self.country_id.code == 'FR' and self.zip and len(self.zip) == 5:
            dept_code = self.zip[:2]
            
            # Cas spéciaux
            if dept_code == '20': # Cas spéciaux pour la Corse 
                dept_code = '2A' if self.zip[:3] <= '201' else '2B' # Cas spéciaux pour la Corse 
            elif dept_code in ['97', '98']: # Cas spéciaux pour les DOM dont la Guadeloupe et la Martinique
                dept_code = self.zip[:3] # Cas spéciaux pour les DOM
            
            department = self.env['res.country.department'].search([
                ('code', '=', dept_code),
                ('country_id.code', '=', 'FR')
            ], limit=1)
            
            if department:
                self.department_id = department.id

    

    @api.model_create_multi
    def create(self, vals_list):
        """Override pour définir le type par défaut à 'delivery' pour les nouveaux contacts"""
        for vals in vals_list:
            if vals.get('parent_id') and not vals.get('type'):
                vals['type'] = 'delivery'
        return super().create(vals_list)

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        """Override pour empêcher la copie automatique de l'adresse du parent pour les sociétés"""
        if not self.is_company:
            # Pour les contacts, on garde le comportement standard
            result = super().onchange_parent_id()
            # On définit le type par défaut à 'delivery' pour les nouveaux contacts
            if not self.type and self.parent_id:
                self.type = 'delivery'
            return result
        # Pour les sociétés, on ne fait rien
        return {}

    @api.onchange('type')
    def onchange_type(self):
        """Empêcher la copie automatique de l'adresse pour les sociétés"""
        if self.is_company:
            return {}
        # Pour les contacts, on copie l'adresse du parent si nécessaire
        if self.parent_id and self.type in ['invoice', 'delivery', 'other']:
            addr = self.parent_id.address_get([self.type])
            if addr[self.type]:
                self.update(self._sync_parent_address(addr[self.type]))
        return {}

    def write(self, vals):
        """Override pour empêcher la synchronisation d'adresse pour les sociétés"""
        if self.is_company and 'parent_id' in vals:
            # Sauvegarde des valeurs d'adresse actuelles
            address_fields = ['street', 'street2', 'city', 'state_id', 'zip', 'country_id']
            current_values = {field: self[field] for field in address_fields if self[field]}
            
            # Exécution du write standard
            result = super().write(vals)
            
            # Restauration des valeurs d'adresse pour les sociétés
            if current_values:
                super().write(current_values)
            return result
            
        return super().write(vals)

    def _sync_parent_address(self, parent):
        """Méthode utilitaire pour synchroniser l'adresse avec le parent"""
        return {
            'street': parent.street,
            'street2': parent.street2,
            'city': parent.city,
            'zip': parent.zip,
            'state_id': parent.state_id.id,
            'country_id': parent.country_id.id,
        }

            