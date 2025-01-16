{
    'name': 'WaterGile Sales',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Gestion avancée des ventes WaterGile',
    'sequence': 1,
    'description': """
        Module de vente WaterGile :
        - One Sale Multiple Delivery
    """,
    'author': 'Dorevia',
    'website': 'https://www.dorevia.com',
    'depends': [
        'sale_management',
        'stock',
        'watergile_partner',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/prev_delivery_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'watergile_sales/static/src/js/toggle_form_view.js',
            'watergile_sales/static/src/scss/toggle_form_view.scss',
        ],
        'web.assets_qweb': [
            'watergile_sales/static/src/xml/toggle_form_view.xml',
        ],
    },
}