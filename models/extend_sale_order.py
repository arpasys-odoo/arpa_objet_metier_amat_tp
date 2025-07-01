# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bon_intervention_ids = fields.One2many('bon_intervention.bon_intervention', 'sale_order_id', string='Bons d\'intervention')
    bon_intervention_count = fields.Integer(compute='_compute_bon_intervention_count', string='Nombre de bons d\'intervention')
    has_maintenance_contract = fields.Boolean(string='Contrat de maintenance', help="Indique si ce devis concerne un contrat de maintenance")
    next_maintenance_date = fields.Date(string='Prochaine maintenance prévue')
    maintenance_frequency = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('semi_annual', 'Semestrielle'),
        ('annual', 'Annuelle'),
    ], string='Fréquence de maintenance')

    @api.depends('bon_intervention_ids')
    def _compute_bon_intervention_count(self):
        for order in self:
            order.bon_intervention_count = len(order.bon_intervention_ids)

    def action_create_bon_intervention(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Veuillez d\'abord sélectionner un client'))

        return {
            'name': _('Nouveau Bon d\'Intervention'),
            'type': 'ir.actions.act_window',
            'res_model': 'bon_intervention.bon_intervention',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.id,
                'default_date_intervention': fields.Date.today(),
            },
        }

    def action_view_bon_interventions(self):
        self.ensure_one()
        return {
            'name': _('Bons d\'Intervention'),
            'type': 'ir.actions.act_window',
            'res_model': 'bon_intervention.bon_intervention',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
        }
