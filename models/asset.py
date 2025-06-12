# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Asset(models.Model):
    _name = 'am.asset'
    _description = "Objet Métier"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _check_company_auto = True

    name = fields.Char(string="Nom de l'objet", required=True, tracking=True)

    # Image de l'objet
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image("Image (petit)", related="image_1920", max_width=128, max_height=128, store=True)

    # Couleur pour l'avatar (style contacts)
    color = fields.Integer(string='Couleur', default=0)

    # Informations générales de l'objet
    marque = fields.Char(string="Marque", required=True, tracking=True)
    modele = fields.Char(string="Modèle", required=True, tracking=True)
    numero_coque = fields.Char(string="Numéro de série / Coque", required=True, tracking=True)

    # Dimensions
    longueur = fields.Float(string="Longueur (m)", tracking=True)
    largeur = fields.Float(string="Largeur (m)", tracking=True)

    # Propulsion
    type_propulsion = fields.Selection([
        ('arbre', 'Arbre'),
        ('embase', 'Embase')
    ], string="Type de propulsion", tracking=True)

    # Moteurs
    nombre_moteurs = fields.Integer(string="Nombre de moteurs", default=1, tracking=True)
    type_moteur = fields.Selection([
        ('inboard', 'Inboard'),
        ('hors_bord', 'Hors-bord')
    ], string="Type de moteur", tracking=True)
    marque_moteur = fields.Char(string="Marque du moteur", tracking=True)
    modele_moteur = fields.Char(string="Modèle du moteur", tracking=True)
    numero_serie_moteur = fields.Char(string="Numéro de série du moteur", tracking=True)
    numero_serie_moteur_babord = fields.Char(string="Numéro de série moteur bâbord", tracking=True)
    numero_serie_moteur_tribord = fields.Char(string="Numéro de série moteur tribord", tracking=True)
    numero_moteur_annexe = fields.Char(string="Numéro moteur annexe", tracking=True)

    # Emplacement
    nom_port = fields.Char(string="Nom de l'emplacement", tracking=True, required=True)
    numero_place = fields.Char(string="Numéro/Référence de place", tracking=True, required=True)

    # Documents annexes
    document_ids = fields.Many2many('ir.attachment', string="Documents annexes",
                                    help="Documents associés à l'objet (PDF, photos, etc.)")

    # Relations
    partner_id = fields.Many2one('res.partner', string="Propriétaire", required=True,
                                 tracking=True, index=True)
    company_id = fields.Many2one('res.company', string="Société", required=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True, string="Actif")

    @api.constrains('name', 'partner_id')
    def _check_unique_name_partner(self):
        for record in self:
            domain = [
                ('name', '=', record.name),
                ('partner_id', '=', record.partner_id.id),
                ('id', '!=', record.id)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_("Un objet avec ce nom existe déjà pour ce client !"))

    @api.constrains('nombre_moteurs')
    def _check_nombre_moteurs(self):
        for record in self:
            if record.nombre_moteurs <= 0:
                raise ValidationError(_("Le nombre de moteurs doit être supérieur à zéro."))

    @api.onchange('nombre_moteurs')
    def _onchange_nombre_moteurs(self):
        """Masquer/afficher les champs relatifs aux multiples moteurs"""
        for record in self:
            if record.nombre_moteurs > 1:
                return {
                    'warning': {
                        'title': _('Plusieurs moteurs'),
                        'message': _(
                            'Veuillez renseigner les numéros de série des moteurs bâbord et tribord dans l\'onglet Moteurs.')
                    }
                }
            else:
                record.numero_serie_moteur_babord = False
                record.numero_serie_moteur_tribord = False