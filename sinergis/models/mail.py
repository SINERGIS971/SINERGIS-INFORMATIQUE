from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import is_html_empty

class MailActivity(models.Model):
    _inherit = "mail.activity"

    def x_sinergis_mail_activity_button_calendar_event(self):
        res_model = self.env.context.get('default_res_model')
        if res_model == "helpdesk.ticket":
            self.ensure_one()
            action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
            res_id = self.env.context.get('default_res_id')
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': res_id,
                'default_res_model': res_model,
                'default_name': self.summary or self.res_name,
                'default_description': self.note if not is_html_empty(self.note) else '',
                'default_activity_ids': [(6, 0, self.ids)],
                'default_x_sinergis_calendar_event_client': self.env['helpdesk.ticket'].search([('id','=',res_id)]).partner_id.id,
                'default_x_sinergis_calendar_event_contact_transfered': self.env['helpdesk.ticket'].search([('id','=',res_id)]).x_sinergis_helpdesk_ticket_contact.id,
            }
            return action
        if res_model == "project.task":
            self.ensure_one()
            action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
            res_id = self.env.context.get('default_res_id')
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': res_id,
                'default_res_model': res_model,
                'default_name': self.env['project.task'].search([('id','=',res_id)]).name,
                'default_description': self.note if not is_html_empty(self.note) else '',
                'default_activity_ids': [(6, 0, self.ids)],
                'default_x_sinergis_calendar_event_client': self.env['project.task'].search([('id','=',res_id)]).partner_id.id,
                'default_x_sinergis_calendar_event_facturation': 'Devis',
                'default_x_sinergis_calendar_event_project_transfered': self.env['project.task'].search([('id','=',res_id)]).project_id.id,
                'default_x_sinergis_calendar_event_tache_transfered': self.env['project.task'].search([('id','=',res_id)]).id,
            }
            return action
        if res_model == "res.partner":
            self.ensure_one()
            action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
            res_id = self.env.context.get('default_res_id')
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': res_id,
                'default_res_model': res_model,
                'default_name': self.env['project.task'].search([('id','=',res_id)]).name,
                'default_description': self.note if not is_html_empty(self.note) else '',
                'default_activity_ids': [(6, 0, self.ids)],
                'default_x_sinergis_calendar_event_client': self.env['res.partner'].search([('id','=',res_id)]).id
            }
            return action
        else:
            self.ensure_one()
            action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': self.env.context.get('default_res_id'),
                'default_res_model': self.env.context.get('default_res_model'),
                'default_name': self.summary or self.res_name,
                'default_description': self.note if not is_html_empty(self.note) else '',
                'default_activity_ids': [(6, 0, self.ids)],
            }
            return action
