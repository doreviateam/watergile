from odoo import SUPERUSER_ID, api

def pre_init_hook(env):
    # Configuration de l'euro
    env.cr.execute("""
        UPDATE res_company 
        SET currency_id = (SELECT id FROM res_currency WHERE name = 'EUR')
        WHERE id = 1
    """)

def post_init_hook(env):
    # Configuration de l'adresse française
    company = env['res.company'].browse(1)
    france = env.ref('base.fr')
    if france:
        company.write({
            'country_id': france.id,
            'state_id': False,
            'city': 'Nantes',
            'zip': '44000',
            'street': '1 rue de l\'Innovation',
        })
        print("Adresse de la société mise à jour!")