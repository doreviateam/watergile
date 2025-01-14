from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Champs métier
    siret = fields.Char(
        string="SIRET",
        help="Numéro SIRET de l'établissement"
    )
    siren = fields.Char(
        string="SIREN",
        readonly=True,
        help="Identifiant SIREN (9 premiers chiffres du SIRET)"
    )
    enseigne = fields.Char(
        string="Enseigne commerciale",
        readonly=True
    )
    activite_principale = fields.Char(
        string="Code NAF",
        readonly=True
    )
    last_insee_sync = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )
    # Ajout des champs de géolocalisation
    latitude = fields.Float(
        string="Latitude",
        digits=(16, 5),
        readonly=True
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(16, 5),
        readonly=True
    )

    @api.onchange('siret')
    def _onchange_siret(self):
        """Synchronisation avec l'INSEE lors de la modification du SIRET"""
        if not self.siret or len(self.siret.strip()) != 14:
            return

        try:
            # Création du service de synchronisation
            sync_service = self.env['insee.sync.service'].create({
                'siret': self.siret.strip()
            })
            
            # Récupération des données
            company_data = sync_service.sync_company_data()
            
            if company_data:
                # Sauvegarde du N° TVA
                current_vat = self.vat
                
                # Mise à jour des données d'adresse
                address = company_data.get('address', {})
                self.update({
                    'street': address.get('street'),
                    'street2': address.get('street2'),
                    'zip': address.get('zip'),
                    'city': address.get('city'),
                    'country_id': address.get('country_id'),
                })
                
                # Mise à jour des autres informations
                self.update({
                    'name': company_data.get('name'),
                    'siren': company_data.get('siren'),
                    'activite_principale': company_data.get('activity'),
                    'last_insee_sync': fields.Datetime.now(),
                })
                
                # Restauration du N° TVA
                self.vat = current_vat
                
        except Exception as e:
            _logger.error(f"Erreur synchronisation INSEE: {str(e)}")
            return {
                'warning': {
                    'title': _('Erreur de synchronisation'),
                    'message': str(e)
                }
            }
    
    