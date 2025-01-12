from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    relation_description = fields.Char(
        string="Description de la relation",
        help="Description complémentaire de la relation"
    )

    # Le type calculé reste comme avant
    company_type_display = fields.Char(
        string='Type',
        compute='_compute_company_type_display',
        store=True
    )

    hierarchy_type = fields.Selection([
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

    region_id = fields.Many2one(
        'res.region', 
        string='Région',
        ondelete='restrict'
    )

    @api.model
    def _valid_field_parameter(self, field, name):
        return name in ['widget', 'options'] or super()._valid_field_parameter(field, name)

    partner_blaz_id = fields.Many2one(
        'partner.blaz',
        string='Blaz',
        help='Blaz associé à ce partenaire'
    )

    company_info_display = fields.Char(
        string='Information',
        compute='_compute_company_type_display',
        store=True
    )

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

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.country_id = self.department_id.country_id
            self.state_id = self.department_id.state_id

    @api.onchange('zip', 'country_id')
    def _onchange_zip_country(self):
        if self.country_id.code == 'FR' and self.zip and len(self.zip) == 5:
            dept_code = self.zip[:2]
            
            # Cas spéciaux
            if dept_code == '20':
                dept_code = '2A' if self.zip[:3] <= '201' else '2B'
            elif dept_code in ['97', '98']:
                dept_code = self.zip[:3]
            
            department = self.env['res.country.department'].search([
                ('code', '=', dept_code),
                ('country_id.code', '=', 'FR')
            ], limit=1)
            
            if department:
                self.department_id = department.id

    @api.depends('parent_id', 'child_ids', 'type', 'parent_id.type')
    def _compute_company_type_display(self):
        for record in self:
            if not record.parent_id and record.child_ids:
                record.company_type_display = 'Maison mère'
            elif record.type == 'headquarters' and record.parent_id.type == 'headquarters':
                record.company_type_display = 'Antenne'
            else:
                record.company_type_display = dict(record._fields['type'].selection).get(record.type, 'Autre')

            record.company_info_display = False
            is_antenne = (record.type == 'headquarters' and 
                         record.parent_id.type == 'headquarters')
            if is_antenne:
                record.company_info_display = 'Antenne'

    @api.model
    def _install_hierarchy_type(self):
        """Migration des données de relation_type vers hierarchy_type"""
        self.env.cr.execute("""
            UPDATE res_partner 
            SET hierarchy_type = relation_type 
            WHERE hierarchy_type IS NULL 
            AND relation_type IN ('other', 'agency', 'headquarters')
        """)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_id') and vals.get('is_company'):
                vals['type'] = 'delivery'
        return super().create(vals_list)

            