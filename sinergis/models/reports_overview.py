from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = "mail.message"
    x_sinergis_partner_company_id = fields.Many2one("res.partner",string="Client",compute="_compute_x_sinergis_partner_company_id",store=True)
    x_sinergis_report_origin = fields.Char(string="Origine", compute="_compute_x_sinergis_report_origin",store=True)

    x_sinergis_signed_reports = fields.One2many('ir.attachment',compute="_compute_x_sinergis_signed_reports",string="Documents échangés")
    x_sinergis_calendar_signed_reports = fields.One2many('calendar.sinergis_intervention_report_done', compute="_compute_x_sinergis_calendar_signed_reports", string="Rapports signés dans le calendrier")

    @api.depends("x_sinergis_partner_company_id")
    def _compute_x_sinergis_partner_company_id (self):
        for rec in self:
            if rec.author_id.parent_id :
                rec.x_sinergis_partner_company_id = rec.author_id.parent_id
            elif rec.author_id.is_company:
                rec.x_sinergis_partner_company_id = rec.author_id
            else :
                partner_company_id = False
                for partner_id in rec.partner_ids:
                    if partner_id != rec.author_id and partner_id.email != rec.author_id.email:
                        if partner_id.parent_id:
                            partner_company_id = partner_id.parent_id
                        else :
                            partner_company_id = partner_id
                rec.x_sinergis_partner_company_id = partner_company_id
            
    @api.depends("x_sinergis_report_origin")
    def _compute_x_sinergis_report_origin (self):
        for rec in self:
            x_sinergis_report_origin = ""
            if rec.model == "helpdesk.ticket":
                x_sinergis_report_origin = f"Ticket {str(rec.res_id)}"
            elif rec.model == "calendar.event":
                x_sinergis_report_origin = f"Événement {str(rec.res_id)}"
            rec.x_sinergis_report_origin = x_sinergis_report_origin

    @api.depends("x_sinergis_signed_reports")
    def _compute_x_sinergis_signed_reports(self):
        for rec in self:
            x_sinergis_signed_reports = []
            message_ids = self.env['mail.message'].search([('x_sinergis_report_origin','=',rec.x_sinergis_report_origin)])
            for message_id in message_ids:
                for attachment_id in message_id.attachment_ids:
                    x_sinergis_signed_reports.append(attachment_id.id)
            rec.x_sinergis_signed_reports = x_sinergis_signed_reports

    @api.depends("x_sinergis_calendar_signed_reports")
    def _compute_x_sinergis_calendar_signed_reports (self):
        for rec in self:
            if rec.model == "calendar.event":
                rec.x_sinergis_calendar_signed_reports = self.env["calendar.sinergis_intervention_report_done"].search([("event_id",'=',rec.res_id)])
            else:
                rec.x_sinergis_calendar_signed_reports = False
                

    def x_sinergis_open (self):
        context = {}
        if self.model == "helpdesk.ticket":
            context = {
            'name': 'Assistance',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id': self.env['helpdesk.ticket'].search([('id', '=', self.res_id)]).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }
        elif self.model == "calendar.event":
            context = {
            'name': 'Calendrier',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'calendar.event',
            'res_id': self.env['calendar.event'].search([('id', '=', self.res_id)]).id,
            'target': 'new',
            'flags':{'mode':'readonly'},
            }
        return context
    



