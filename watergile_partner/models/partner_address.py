from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_delivery_address = fields.Boolean(string="Est une adresse de livraison", default=False)
    has_delivery_address = fields.Boolean(
        string="A une adresse de livraison",
        compute='_compute_has_delivery_address',
        store=True
    )

    @api.depends('child_ids', 'child_ids.type')
    def _compute_has_delivery_address(self):
        for partner in self:
            partner.has_delivery_address = bool(partner.child_ids.filtered(lambda c: c.type == 'delivery'))

    @api.model_create_multi
    def create(self, vals_list):
        """Créer automatiquement une adresse de livraison"""
        # Si la création est due à une copie, ne créer pas l'adresse de livraison
        if self.env.context.get('skip_delivery_creation'):
            return super().create(vals_list)
        
        # Créer d'abord les partenaires principaux
        partners = super().create(vals_list)
        
        # Pour chaque partenaire créé
        for partner, vals in zip(partners, vals_list):
            # Vérifier si c'est une société, pas une adresse de livraison, et qu'il n'a pas déjà une adresse de livraison
            if (vals.get('is_company') and 
                not vals.get('is_delivery_address') and 
                not partner.child_ids.filtered(lambda c: c.type == 'delivery')):
                
                delivery_vals = {
                    'name': f"Livraison",
                    'is_company': False,
                    'type': 'delivery',
                    'parent_id': partner.id,
                    'is_delivery_address': True,
                    'street': partner.street,
                    'street2': partner.street2,
                    'zip': partner.zip,
                    'city': partner.city,
                    'state_id': partner.state_id.id if partner.state_id else False,
                    'country_id': partner.country_id.id if partner.country_id else False,
                }
                
                # Créer l'adresse de livraison
                self.env['res.partner'].with_context(skip_delivery_creation=True).create(delivery_vals)
        
        return partners
    
    @api.onchange('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def _onchange_address_fields(self):
        self.ensure_one()
        if self.child_ids:
            for child in self.child_ids.filtered(lambda c: c.type == 'delivery'):
                child.write({
                    'street': self.street,
                    'street2': self.street2,
                    'zip': self.zip,
                    'city': self.city,
                    'state_id': self.state_id.id,
                    'country_id': self.country_id.id
                })

