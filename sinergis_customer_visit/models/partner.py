# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = "res.partner"
    last_visit_date = fields.Datetime("Date de la dernière visite", compute="_compute_partner_visits")
    last_visit_type = fields.Selection([('on_site', 'Sur site'),('phone', 'Par téléphone')], string="Type de visite", compute="_compute_partner_visits")
    visit_state = fields.Selection([('no_visit', 'Pas de visite'),('missing_on_site', 'Manque une visite sur site'),('missing_on_site_or_phone', 'Manque une visite'), ('visited', 'Conditions de visite remplies')], string="Etat", compute="_compute_partner_visits")

    def button_view_partner_visits(self):
        return {
            'name': ('Visites'),
            'type': 'ir.actions.act_window',
            "views": [[self.env.ref('sinergis_customer_visi.sinergis_customer_visit_partner_tree').id, "tree"],[False, "form"]],
            'res_model': 'calendar.event',
            'domain': f"[('partner_id', '=', {self.id})]",
        }

    def button_create_partner_visit(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_res_id': self.id,
            'default_res_model': "res.partner",
            'default_name': "Visite - " + self.partner_id.name,
            'default_x_sinergis_calendar_event_client': self.partner_id.id, # Specificity for Sinergis
            'default_is_visit': True,
        }
        return action

    @api.depends("last_visit_date", "visit_state")
    def _compute_partner_visits (self):
        for rec in self:
            #Date de la dernière visite
            last_visit = self.env["calendar.event"].search([('x_sinergis_calendar_event_client','=',rec.id),('is_visit','=',True)], order='start desc', limit=1)
            if last_visit:
                rec.last_visit_date = last_visit.start
                rec.last_visit_type = last_visit.visit_type
            else:
                rec.last_visit_date = False
                rec.last_visit_type = False

            # Visites les 6 derniers mois
            event_6_ids = self.env["calendar.event"].search([('x_sinergis_calendar_event_client','=',rec.id),
                                                             ('is_visit','=',True),
                                                             ('start','>=',(datetime.now() + relativedelta(months=-6)).strftime('%Y-%m-%d %H:%M:%S')),
                                                             ('start','<=',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))], order='start desc')
            # Visite sur site des 12 derniers mois
            event_12_ids = self.env["calendar.event"].search([('x_sinergis_calendar_event_client','=',rec.id),
                                                             ('is_visit','=',True),
                                                             ('visit_type','=','on_site'),
                                                             ('start','>=',(datetime.now() + relativedelta(months=-12)).strftime('%Y-%m-%d %H:%M:%S')),
                                                             ('start','<=',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))], order='start desc')

            if len(event_6_ids) > 0 and len(event_12_ids) > 0:
                rec.visit_state = "visited"
            elif len(event_6_ids) == 0 and len(event_12_ids) > 0:
                rec.visit_state = "missing_on_site_or_phone"
            elif len(event_6_ids) > 0 and len(event_12_ids) == 0:
                rec.visit_state = "missing_on_site"
            else :
                rec.visit_state = "no_visit"
            

            
            
            

