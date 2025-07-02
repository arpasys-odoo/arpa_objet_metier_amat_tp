# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class BonIntervention(models.Model):
    _name = 'bon_intervention.bon_intervention'
    _description = 'Bon d\'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_intervention desc, id desc'

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nouveau'))
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    asset_id = fields.Many2one('am.asset', string='Machine', tracking=True)
    date_intervention = fields.Date(string='Date d\'intervention', required=True, tracking=True)
    date_order = fields.Date(string='Date de création', default=fields.Date.today, tracking=True)
    lieu_intervention = fields.Char(string='Lieu d\'intervention', tracking=True)
    date_panne = fields.Date(string='Date de panne', tracking=True)
    date_fin_reparation = fields.Date(string='Date fin réparation', tracking=True)

    description = fields.Text(string='Description de l\'intervention', tracking=True)
    detail_panne_intervention = fields.Text(string='Détail panne/intervention', tracking=True)
    fourniture = fields.Text(string='Fournitures utilisées', tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('invoiced', 'Facturé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    technician_id = fields.Many2one('res.users', string='Technicien responsable', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Devis associé', tracking=True)
    sale_order_ids = fields.One2many('sale.order', 'bon_intervention_id', string='Devis/Commandes')
    invoice_ids = fields.One2many('account.move', 'bon_intervention_id', string='Factures')
    maintenance_request_id = fields.Many2one('maintenance.request', string='Demande de maintenance', tracking=True)

    asset_ids = fields.Many2many('am.asset', string='Équipements concernés')
    duration = fields.Float(string='Durée (heures)', tracking=True)
    heures = fields.Float(string='Heures détail', tracking=True)
    total_heure = fields.Float(string='Total heures', compute='_compute_total_heure', store=True)

    signature = fields.Binary(string='Signature du client')
    signature_date = fields.Datetime(string='Date de signature')
    notes = fields.Text(string='Notes internes')

    

    @api.depends('duration', 'heures')
    def _compute_total_heure(self):
        for record in self:
            record.total_heure = (record.duration or 0) + (record.heures or 0)

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('bon_intervention.bon_intervention') or _('Nouveau')
        return super(BonIntervention, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_create_invoice(self):
        if self.state != 'done':
            raise UserError(_('Vous ne pouvez facturer que les bons d\'intervention terminés.'))

        invoice_vals = {
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'bon_intervention_id': self.id,
            'move_type': 'out_invoice',
        }

        invoice = self.env['account.move'].create(invoice_vals)
        self.write({'state': 'invoiced'})

        return {
            'name': _('Facture client'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    def action_create_quotation(self):
        """Créer un devis à partir du bon d'intervention"""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Veuillez d\'abord sélectionner un client'))

        return {
            'name': _('Nouveau Devis'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_bon_intervention_id': self.id,
            },
        }

    def action_view_invoices(self):
        """Voir les factures liées"""
        self.ensure_one()
        return {
            'name': _('Factures'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('bon_intervention_id', '=', self.id)],
        }