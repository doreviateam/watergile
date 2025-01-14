from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PartnerBlaz(models.Model):
    _name = 'partner.blaz'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Partner Blaz'
    
    name = fields.Char(string='Nom', required=True)
    active = fields.Boolean(string='Actif', default=True)
    force_logo_update = fields.Boolean(
        string='Forcer la mise à jour des logos',
        help='Si coché, le logo sera mis à jour pour tous les contacts autorisés, même s\'ils ont déjà un logo',
        default=False
    )
    partner_ids = fields.One2many(
        comodel_name='res.partner', 
        inverse_name='partner_blaz_id', 
        string='Partenaires'
    )     
    image_1920 = fields.Image(
        string='Logo', 
        max_width=1920, 
        max_height=1920,
        required=True,
    )
    image_128 = fields.Image(
        string='Logo miniature', 
        related='image_1920', 
        max_width=128, 
        max_height=128, 
        store=True
    )
    
    owner_partner_id = fields.Many2one(
        'res.partner', 
        string='Propriétaire', 
        required=True,
        domain="[]",
        help='Propriétaire de ce blaz'
    )
    authorized_partner_ids = fields.Many2many(
        'res.partner', 
        string='Contacts autorisés'
    )

    @api.model_create_multi
    def create(self, vals_list):
        blazs = super().create(vals_list)
        for blaz in blazs:
            for partner in blaz.authorized_partner_ids:
                partner.partner_blaz_id = blaz.id
                if not partner.image_1920 or blaz.force_logo_update:
                    partner.image_1920 = blaz.image_1920
        return blazs

    def write(self, vals):
        result = super().write(vals)
        if 'authorized_partner_ids' in vals or 'image_1920' in vals:
            for blaz in self:
                for partner in blaz.authorized_partner_ids:
                    partner.partner_blaz_id = blaz.id
                    if not partner.image_1920 or blaz.force_logo_update:
                        partner.image_1920 = blaz.image_1920
        return result

    @api.constrains('owner_partner_id')
    def _check_owner_type(self):
        for record in self:
            if record.owner_partner_id and not record.owner_partner_id.is_company:
                raise ValidationError(_("Le propriétaire du blaz doit être une société"))

    @api.constrains('partner_ids', 'owner_partner_id')
    def _check_partners_hierarchy(self):
        for record in self:
            for partner in record.partner_ids:
                if partner.parent_id and partner.parent_id != record.owner_partner_id:
                    raise ValidationError(_("Les partenaires doivent être rattachés à la maison mère propriétaire du blaz"))