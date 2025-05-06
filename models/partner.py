# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Compteur de bateaux
    bateau_count = fields.Integer(string='Bateaux', compute='_compute_bateau_count')

    # Nouveaux champs selon la fiche client
    email_contact = fields.Char(string="Email de contact")

    # Champ pour alerte info client
    alerte_info_client = fields.Text(string="Alerte info client",
                                     help="Information importante concernant ce client")

    # Champ pour memo info client
    memo_info_client = fields.Text(string="Mémo info client",
                                   help="Informations diverses concernant ce client")

    # Champ pour le solde financier en cours
    solde_financier = fields.Monetary(string="Solde financier en cours",
                                      compute='_compute_solde_financier', store=False)

    # Champ pour le CA annuel
    ca_client_annuel = fields.Monetary(string="Total CA client annuel",
                                       compute='_compute_ca_client_annuel')

    # Historique CA par année
    ca_historique_ids = fields.One2many('tplb.ca.historique', 'partner_id',
                                        string="Historique CA annuel")

    def _compute_bateau_count(self):
        """Calcule le nombre de bateaux pour chaque partenaire"""
        for partner in self:
            partner.bateau_count = self.env['tplb.bateau'].search_count([('partner_id', '=', partner.id)])

    def action_view_bateaux(self):
        """Action pour afficher les bateaux liés au partenaire"""
        self.ensure_one()
        return {
            'name': _('Bateaux'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'tplb.bateau',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def _compute_solde_financier(self):
        """Calcule le solde financier en cours du client"""
        for partner in self:
            domain = [
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid')
            ]
            invoices = self.env['account.move'].search(domain)
            total = 0
            for invoice in invoices:
                # Pour les factures client
                if invoice.move_type == 'out_invoice':
                    total += invoice.amount_residual
                # Pour les avoirs client
                elif invoice.move_type == 'out_refund':
                    total -= invoice.amount_residual
                # Pour les factures fournisseur
                elif invoice.move_type == 'in_invoice':
                    total -= invoice.amount_residual
                # Pour les avoirs fournisseur
                elif invoice.move_type == 'in_refund':
                    total += invoice.amount_residual
            partner.solde_financier = total

    def _compute_ca_client_annuel(self):
        """Calcule le CA annuel du client pour l'année en cours"""
        for partner in self:
            # Année en cours
            current_year = datetime.now().year
            start_date = datetime(current_year, 1, 1)
            end_date = datetime(current_year, 12, 31)

            # Recherche des factures validées de l'année en cours
            domain = [
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]
            invoices = self.env['account.move'].search(domain)

            # Calcul du CA total
            total_ca = 0
            for invoice in invoices:
                if invoice.move_type == 'out_invoice':
                    total_ca += invoice.amount_total
                elif invoice.move_type == 'out_refund':
                    total_ca -= invoice.amount_total

            partner.ca_client_annuel = total_ca

            # Mise à jour ou création de l'historique CA pour l'année en cours
            ca_historique = self.env['tplb.ca.historique'].search([
                ('partner_id', '=', partner.id),
                ('year', '=', current_year)
            ], limit=1)

            if ca_historique:
                ca_historique.write({'amount': total_ca})
            else:
                self.env['tplb.ca.historique'].create({
                    'partner_id': partner.id,
                    'year': current_year,
                    'amount': total_ca
                })

    # Planifier le calcul du CA à la fin de chaque mois
    @api.model
    def _cron_calculate_annual_ca(self):
        """Cron job pour calculer le CA annuel de tous les clients"""
        partners = self.search([])
        partners._compute_ca_client_annuel()


class PartnerCAHistorique(models.Model):
    _name = 'tplb.ca.historique'
    _description = "Historique du CA annuel par client"
    _order = "year desc"

    partner_id = fields.Many2one('res.partner', string="Client", required=True, ondelete='cascade')
    year = fields.Integer(string="Année", required=True)
    amount = fields.Monetary(string="Montant CA", required=True)
    currency_id = fields.Many2one(related='partner_id.currency_id')

    _sql_constraints = [
        ('unique_partner_year', 'UNIQUE(partner_id, year)',
         'Un seul enregistrement par client et par année est autorisé.')
    ]