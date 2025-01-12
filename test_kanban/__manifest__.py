{
    'name': 'Test Kanban',
    'version': '17.0.1.0.0',
    'summary': 'Test Kanban',
    'description': 'Module de test pour isoler le problème de kanban',
    'category': 'Services/Project',
    'depends': [
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/test_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
