# -*- coding: utf-8 -*-
{
    'name': "Amat TP - Gestion d'Objets Métier",
    'summary': "Gestion des objets métier, bons d'intervention et extension des devis et contacts",
    'description': """
Ce module permet de:
- Gérer des objets métier pour les clients
- Créer et gérer des bons d'intervention
- Étendre les fonctionnalités des devis et contacts

Fonctionnalités:
- Enregistrement des informations des objets (biens, équipements, etc.)
- Association d'un objet à un client
- Gestion des informations techniques (caractéristiques, dimensions, emplacement)
- Fiche client améliorée avec CA annuel, historique, et alertes
- Gestion complète des bons d'intervention
    """,
    'author': "Léo - Arpasys",
    'website': "https://studio.arpasys.com/",
    'category': 'Tools',
    'version': '1.0',
    'depends': [
        'base',
        'mail',
        'account',
        'maintenance',
        'sale',
        'product',
        'contacts',
    ],
    'data': [
        # Sécurité d'abord
        'security/am_asset_security.xml',
        'security/ir.model.access.csv',

        # Données de base
        'data/ir_sequence_data.xml',
        'data/ir_cron.xml',

        # Vues dans l'ordre de dépendance
        'views/machine_type_views.xml',
        'views/asset_views.xml',
        'views/bon_intervention_views.xml',
        'views/maintenance_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'views/hide_native_menu.xml',
        'views/maintenance_integration_views.xml',
    ],
    'assets': {
        'web.assets_backend': [],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': "LGPL-3",
    'sequence': -100,
}