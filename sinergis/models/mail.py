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
            facturation = "Contrat heure" if ("HEURES" in self.env['project.task'].search([('id','=',res_id)]).name) else "Devis"
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': res_id,
                'default_res_model': res_model,
                'default_name': self.env['project.task'].search([('id','=',res_id)]).name,
                'default_description': self.note if not is_html_empty(self.note) else '',
                'default_activity_ids': [(6, 0, self.ids)],
                'default_x_sinergis_calendar_event_client': self.env['project.task'].search([('id','=',res_id)]).partner_id.id,
                'default_x_sinergis_calendar_event_facturation': facturation,
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

class MailMail(models.Model):
    _inherit = "mail.mail"
    
    x_sinergis_has_attachment = fields.Boolean(string="Pièce jointe ?", compute="_compute_x_sinergis_has_attachment")
    x_sinergis_attachment_ids = fields.One2many(
                                                 'ir.attachment',
                                                  compute="_compute_x_sinergis_attachment_ids",
                                                  string='Attachments',
                                                  help='Attachments are linked to a document through model / res_id and to the message '
                                                        'through this field.')
    x_sinergis_email_list = fields.Char(string="Liste des emails", compute="_compute_x_sinergis_email_list")

    @api.depends("x_sinergis_attachment_ids")
    def _compute_x_sinergis_attachment_ids(self):
        for rec in self:
            if rec.mail_message_id:
                if rec.mail_message_id.record_name == "False":
                    rec.x_sinergis_attachment_ids = False
                else:
                    rec.x_sinergis_attachment_ids = rec.attachment_ids
            else:
                rec.x_sinergis_attachment_ids = False

    @api.depends("x_sinergis_has_attachment")
    def _compute_x_sinergis_has_attachment (self):
        for rec in self:
            if len(rec.attachment_ids) > 1:
                rec.x_sinergis_has_attachment = True
            elif len(rec.attachment_ids) == 1:
                if rec.attachment_ids[0].name == "image0":
                    rec.x_sinergis_has_attachment = False
                else :
                    rec.x_sinergis_has_attachment = True
            else:
                rec.x_sinergis_has_attachment = False

    @api.depends("x_sinergis_email_list")
    def _compute_x_sinergis_email_list (self):
        for rec in self:
            if rec.email_to:
                recipient_ids_email = rec.email_to.split(',')
            else :
                recipient_ids_email = []
            for recipient_id in rec.recipient_ids:
                recipient_ids_email.append(recipient_id.email)
            if len(recipient_ids_email)>0:
                rec.x_sinergis_email_list = ','.join(recipient_ids_email)
            else:
                rec.x_sinergis_email_list = False

    @api.model
    def send(self, auto_commit=False, raise_exception=False):
        result = super(MailMail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)
        for mail in self:
            # Marquer le Rapport d'intervention comme envoyé.
            if len(self.env['mail.mail'].search([('id','=',mail.id)])) > 0:
                if hasattr(mail, 'subject') and hasattr(mail, 'res_id'):
                    if "Rapport d'intervention" in mail.subject:
                        if mail.model == "helpdesk.ticket":
                            self.env['helpdesk.ticket'].search([('id','=',mail.res_id)]).action_x_sinergis_helpdesk_ticket_sent_report(mail)
                        elif mail.model == "calendar.event":
                            self.env['calendar.event'].search([('id','=',mail.res_id)]).action_x_sinergis_calendar_event_sent_report(mail)
        return result



class MailMessage(models.Model):
    _inherit = "mail.message"

    x_sinergis_has_destination = fields.Boolean(compute="_compute_x_sinergis_has_destination")

    @api.depends('x_sinergis_has_destination')
    def _compute_x_sinergis_has_destination (self):
        for rec in self:
            if len(rec.notification_ids) > 0:
                rec.x_sinergis_has_destination = True
            else:
                rec.x_sinergis_has_destination = False
