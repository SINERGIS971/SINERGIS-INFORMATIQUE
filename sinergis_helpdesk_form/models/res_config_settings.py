# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable = fields.Boolean(string="Activer le formulaire en ligne",
                            config_parameter='sinergis_helpdesk_form.enable')
    max_files = fields.Integer(string="Nombre max. de fichiers pour un ticket",
                            config_parameter='sinergis_helpdesk_form.max_files')
    max_file_size = fields.Integer(string="Taille maximale par fichier (octet)",
                            config_parameter='sinergis_helpdesk_form.max_file_size')
    client_key = fields.Char(string="Clé serveur",
                            config_parameter='sinergis_helpdesk_form.client_key')
    server_key = fields.Char(string="Clé serveur",
                            config_parameter='sinergis_helpdesk_form.server_key')