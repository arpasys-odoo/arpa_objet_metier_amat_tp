# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    asset_id = fields.Many2one('am.asset', string='Machine',
                               help="Machine concernée par la demande de maintenance",
                               index=True, tracking=True)

    partner_id = fields.Many2one('res.partner', string='Client',
                                 related='asset_id.partner_id',
                                 store=True, readonly=True,
                                 help="Client propriétaire de la machine")

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        if self.asset_id:
            self.equipment_id = False
            self.name = _("Maintenance Request for %s - %s") % (self.asset_id.name, self.asset_id.numero_serie)
        else:
            self.name = False