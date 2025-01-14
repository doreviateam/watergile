{
    'name': 'Watergile Partner',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Extension des partenaires pour la gestion de groupes',
    'description': """
        Extension du module res.partner pour gérer :
        - Maison mère
        - Sièges
        - Antennes
        - Filiales
        - Blaz et organisation
    """,
    'depends': [
        'base',
        'contacts',
        'hr',
        'watergile_web',
        'l10n_fr_department',
        'l10n_fr_state',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/watergile_security.xml',
        'data/res_user_david_data.xml',
        'views/res_partner.xml',
        'views/partner_blaz_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}