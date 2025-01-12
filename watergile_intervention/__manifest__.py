{
    'name': 'WaterGile Intervention',
    'version': '17.0.1.0.0',
    'summary': 'Watergile Intervention',
    'description': 'Gestion des interventions',
    'author': 'Doreviateam',
    'category': 'Services/Project',
    'depends': [
        'base',
        'base_setup',
        'product',
        'contacts',
        'sale',
        'sale_management',
        'sale_project',
        'watergile_base'
    ],
    'data': [
        'security/watergile_intervention_security.xml',
        'security/ir.model.access.csv',
        'sequences/intervention_sequence.xml',
        'views/intervention_views.xml',
        'views/sale_order_views.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 1,
}