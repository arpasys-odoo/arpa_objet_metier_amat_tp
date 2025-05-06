# -*- coding: utf-8 -*-
{
    'name': "TPLB Bateau",

    'summary': "Gestion des bateaux des clients",

    'description': """
Ce module permet de gérer les bateaux des clients.
Fonctionnalités:
- Enregistrement des informations des bateaux
- Association d'un bateau à un client
- Gestion des informations techniques (moteurs, dimensions, emplacement)
- Fiche client améliorée avec CA annuel, historique, type de client et alertes
    """,

    'author': "Léo",
    'website': "https://studio.arpasys.com/",

    'category': 'Nautique',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
    ],

    # always loaded
    'data': [
        'security/tplb_bateau_security.xml',
        'security/ir.model.access.csv',

        'data/ir_cron.xml',

        'views/bateau_views.xml',
        'views/partner_views.xml',
        'views/menu_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'tplb_bateau/static/src/scss/style.scss',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': "LGPL-3",
    'sequence': -100,
}