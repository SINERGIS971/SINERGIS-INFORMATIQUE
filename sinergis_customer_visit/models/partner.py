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
            "views": [[self.env.ref('sinergis_customer_visit.sinergis_calendar_event_visit_tree').id, "tree"],[False, "form"]],
            'res_model': 'calendar.event',
            'domain': f"[('x_sinergis_calendar_event_client', '=', {self.id}), ('is_visit', '=', True)]",
        }

    def button_create_partner_visit(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_res_id': self.id,
            'default_res_model': "res.partner",
            'default_name': "Visite - " + self.name,
            'default_x_sinergis_calendar_event_client': self.id, # Specificity for Sinergis
            'default_is_visit': True,
            'create': True
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

            # Visite sur site des 12 derniers mois
            event_12_id = self.env["calendar.event"].search([('x_sinergis_calendar_event_client','=',rec.id),
                                                             ('is_visit','=',True),
                                                             ('visit_type','=','on_site'),
                                                             ('start','>=',(datetime.now() + relativedelta(months=-12)).strftime('%Y-%m-%d %H:%M:%S')),
                                                             ('start','<=',datetime.now().strftime('%Y-%m-%d 23:59:59'))], order='start asc', limit=1)
            # Visites les 6 derniers mois
            event_6_ids = self.env["calendar.event"].search([('id','!=',event_12_id.id),
                                                             ('x_sinergis_calendar_event_client','=',rec.id),
                                                             ('is_visit','=',True),
                                                             ('start','>=',(datetime.now() + relativedelta(months=-6)).strftime('%Y-%m-%d %H:%M:%S')),
                                                             ('start','<=',datetime.now().strftime('%Y-%m-%d 23:59:59'))], order='start desc')

            visit_6_months = False
            visit_site_12_months = False
            if event_12_id :
                visit_site_12_months = True
            if len(event_6_ids) > 0:
                visit_6_months = True
            
            # Client considéré comme visité si au moins une visite sur site dans les 12 mois ET une visite les 6 derniers mois
            if visit_6_months and visit_site_12_months:
                rec.visit_state = "visited"
            elif visit_6_months and not visit_site_12_months:
                rec.visit_state = "missing_on_site"
            elif not visit_6_months and visit_site_12_months:
                rec.visit_state = "missing_on_site_or_phone"
            else:
                rec.visit_state = "no_visit"
