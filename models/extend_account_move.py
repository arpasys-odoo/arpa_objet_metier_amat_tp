# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    bon_intervention_id = fields.Many2one(
        'bon_intervention.bon_intervention', string='Bon d\'Intervention',
        help="Bon d\'Intervention à l\'origine de cette facture",
        index=True, ondelete='set null')
