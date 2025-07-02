# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AmAsset(models.Model):
    _name = 'am.asset'
    _description = "Machine"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, numero_parc'

    # --- Identification & Informations Générales ---
    name = fields.Char(string="Désignation de la machine", required=True, tracking=True,
                       help="Ex: Pelle sur chenilles 320T, Chargeuse sur pneus 950M...")
    active = fields.Boolean(default=True, string="Actif")

    # Image de la machine
    image_1920 = fields.Image(string="Photo de la machine", max_width=1920, max_height=1920)
    image_128 = fields.Image("Vignette", related="image_1920", max_width=128, max_height=128, store=True)

    # Propriétaire et Société
    partner_id = fields.Many2one('res.partner', string="Client Propriétaire", required=True, tracking=True, index=True)

    # --- Classification & Spécifications ---
    type_machine_id = fields.Many2one('am.machine.type', string="Type de machine", required=True, tracking=True)

    marque = fields.Char(string="Marque", required=True, tracking=True, help="Ex: Caterpillar, Volvo, Komatsu...")
    modele = fields.Char(string="Modèle", required=True, tracking=True, help="Ex: 320, 966M, D6T...")
    numero_serie = fields.Char(string="Numéro de série (VIN)", required=True, tracking=True,
                               help="Numéro d'identification unique de la machine.")
    numero_parc = fields.Char(string="Numéro de parc client", tracking=True,
                              help="Référence interne de la machine chez le client.")

    # --- Données Techniques & Opérationnelles ---
    annee_fabrication = fields.Integer(string="Année de fabrication")
    compteur_horaire = fields.Float(string="Compteur horaire (h)", tracking=True,
                                    help="Nombre total d'heures de fonctionnement.")
    date_releve_horaire = fields.Date(string="Date du dernier relevé horaire", tracking=True)
    poids_operationnel = fields.Float(string="Poids opérationnel (kg)",
                                      help="Poids de la machine en ordre de marche.")

    # --- Motorisation ---
    marque_moteur = fields.Char(string="Marque du moteur", tracking=True)
    modele_moteur = fields.Char(string="Modèle du moteur", tracking=True)
    numero_serie_moteur = fields.Char(string="Numéro de série du moteur", tracking=True)

    # --- Emplacement & Statut ---
    emplacement_actuel = fields.Text(string="Emplacement actuel / Chantier", tracking=True,
                                     help="Lieu où se trouve la machine (adresse, nom du chantier...).")
    personne_contact = fields.Char(string="Contact sur site",
                                   help="Nom et téléphone du responsable de la machine sur le site.")

    # --- Contrats & Suivi ---
    contrat_maintenance_id = fields.Many2one('sale.order', string="Contrat de maintenance",
                                             domain=[('has_maintenance_contract', '=', True)])
    prochaine_maintenance_date = fields.Date(string="Prochaine maintenance préventive")
    prochaine_maintenance_heures = fields.Float(string="Prochaine maintenance (heures)",
                                                 help="Seuil horaire pour la prochaine maintenance.")

    # --- Historique & Documents ---
    document_ids = fields.Many2many('ir.attachment', string="Documents techniques",
                                    help="Manuels, schémas, certificats de conformité, etc.")
    intervention_ids = fields.One2many('bon_intervention.bon_intervention', 'asset_id',
                                       string="Historique des interventions")
    intervention_count = fields.Integer(string="Nombre d'interventions", compute='_compute_intervention_count')
    maintenance_request_ids = fields.One2many('maintenance.request', 'asset_id',
                                              string="Demandes de maintenance")

    # Contrainte pour l'unicité
    _sql_constraints = [
        ('numero_serie_uniq', 'unique(numero_serie)',
         'Ce numéro de série est déjà enregistré pour une autre machine !')
    ]

    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for asset in self:
            asset.intervention_count = len(asset.intervention_ids)

    def action_view_interventions(self):
        """Action pour afficher les interventions liées à cette machine"""
        self.ensure_one()
        return {
            'name': _('Interventions'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'bon_intervention.bon_intervention',
            'domain': [('asset_id', '=', self.id)],
            'context': {
                'default_asset_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }

    @api.constrains('numero_parc', 'partner_id')
    def _check_unique_parc_number_partner(self):
        for record in self:
            if record.numero_parc and record.partner_id:
                domain = [
                    ('numero_parc', '=', record.numero_parc),
                    ('partner_id', '=', record.partner_id.id),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(_("Ce numéro de parc existe déjà pour ce client !"))