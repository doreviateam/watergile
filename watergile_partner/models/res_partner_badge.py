from odoo import models, fields, api

class ResPartnerBadge(models.Model):
    _name = 'res.partner.badge'
    _description = 'Badge pour les partenaires'

    name = fields.Char(string='Nom', help="Nom du badge")
    active = fields.Boolean(string='Actif', default=True, help="Active le badge")
    description = fields.Text(string='Description', help="Description du badge")
    color = fields.Char(string='Couleur', help="Couleur du badge")
    partner_ids = fields.Many2many(comodel_name='res.partner', 
                                   relation='res_partner_badge_rel',
                                   column1='badge_id',
                                   column2='partner_id',
                                   string='Partenaires', help="Partenaires associés au badge")
    
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    badge_ids = fields.Many2many(comodel_name='res.partner.badge', # OK
                                 relation='res_partner_badge_rel',
                                 column1='partner_id',
                                 column2='badge_id',
                                 string='Badges', help="Badges associés au partenaire")
    
    # company_info_display = fields.Char(string='Information', compute='_compute_company_type_display', store=True, index=True, help="Information complémentaire de l'entité")
    
    # Calcule l'attribution de badge en fontion de la relation hierarchique entre une entité et sa mère 
    company_badge_display = fields.Char(string='Badge', # OK
                                        compute='_compute_company_badge_display', store=True, index=True, help="Badge de l'entité")

    badge_color = fields.Char(string='Couleur du badge', compute='_compute_company_badge_display', store=True)
    
    hierarchy_relation = fields.Selection([ # OK
        ('other', 'Autre'),
        ('agency', 'Agence'),
        ('headquarters', 'Siège')
    ], string='Établissement', 
       default='other',
       help="Définit le type d'établissement dans la structure organisationnelle :\n"
            "* Établissement principal : Siège de l'entreprise\n"
            "* Établissement secondaire : Agence ou succursale\n"
            "* Autre établissement : Autre type de structure\n\n"
            "Note : Ce type est différent des types d'adresses standards qui servent à la logistique et l'administration.")


    @api.depends('parent_id', 'child_ids', 'hierarchy_relation', 'parent_id.hierarchy_relation')
    def _compute_company_badge_display(self):
        """Permet de définir les badges en fonction de la relation hierarchique"""

        # Si ce n'est pas une société, on ne peut pas avoir de badge
        for record in self:
            if not record.is_company:
                record.company_badge_display = False
                record.badge_color = False
                continue
            
            # Maison mère : pas de parent, avec enfants dont au moins un est une société, type 'other'
            if not record.parent_id and record.child_ids and record.hierarchy_relation == 'other':
                # Vérifier si au moins un enfant est une société
                if any(child.is_company for child in record.child_ids):
                    record.company_badge_display = 'Maison mère'
                    record.badge_color = 'primary'  # Bleu
                else:
                    record.company_badge_display = False
                    record.badge_color = False

            # Filiale : parent type 'other', type 'other'
            elif record.parent_id and record.parent_id.hierarchy_relation == 'other' and record.hierarchy_relation == 'other':
                record.company_badge_display = 'Filiale'
                record.badge_color = 'success'  # Vert

            # Siège : parent type 'other', type 'headquarters'
            elif record.parent_id and record.parent_id.hierarchy_relation == 'other' and record.hierarchy_relation == 'headquarters':
                record.company_badge_display = 'Siège'
                record.badge_color = 'warning'  # Orange

            # Agence : parent type 'other', type 'agency'
            elif record.parent_id and (record.parent_id.hierarchy_relation == 'other' or record.parent_id.hierarchy_relation == 'headquarters') and record.hierarchy_relation == 'agency':
                record.company_badge_display = 'Agence'
                record.badge_color = 'info'  # Bleu clair

            # Antenne : parent type 'headquarters', type 'headquarters'
            elif record.parent_id and record.parent_id.hierarchy_relation == 'headquarters' and record.hierarchy_relation == 'headquarters':
                record.company_badge_display = 'Antenne'
                record.badge_color = 'warning'  # C'est un siège qui est pilote par un autre siège

            # Si ce n'est pas une société, on ne peut pas avoir de badge
            else:
                record.company_badge_display = False
                record.badge_color = False
