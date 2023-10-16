from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = "mail.message"
    x_sinergis_partner_company_id = fields.Many2one("res.partner",string="Société du client",compute="_compute_x_sinergis_partner_company_id",store=True)
    x_sinergis_report_origin = fields.Char(string="Origine", compute="_compute_x_sinergis_report_origin",store=True)

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

    



