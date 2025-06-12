# -*- coding: utf-8 -*-
{
    'name': "Gestion d'Objets Métier",

    'summary': "Gestion générique d'objets ou biens appartenant aux clients",

    'description': """
Ce module permet de gérer des objets métier pour les clients.
Fonctionnalités:
- Enregistrement des informations des objets (biens, équipements, etc.)
- Association d'un objet à un client
- Gestion des informations techniques (caractéristiques, dimensions, emplacement)
- Fiche client améliorée avec CA annuel, historique, et alertes
    """,

    'author': "Léo",
    'website': "https://studio.arpasys.com/",

    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
    ],

    # always loaded
    'data': [
        'security/am_asset_security.xml',
        'security/ir.model.access.csv',

        'data/ir_cron.xml',

        'views/asset_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': "LGPL-3",
    'sequence': -100,
}