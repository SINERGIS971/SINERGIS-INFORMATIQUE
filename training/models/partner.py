from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    training_count = fields.Integer(compute="_compute_training_count")

    @api.depends("training_count")
    def _compute_training_count(self):
        for rec in self:
            rec.training_count = self.env['training'].sudo().search_count([('partner_id', '=', rec.id)])

     #ACCES AUX FORMATIONS LIEES AU CLIENT
    def action_view_training(self):
        training_ids = self.env["training"].sudo().search([("partner_id", "=", self.id)])
        ids_list = []
        for training_id in training_ids:
            ids_list.append(training_id.id)
        return {
            'name': ('Formations'),
            'type': 'ir.actions.act_window',
            "views": [[False, "tree"],[False, "form"]],
            'res_model': 'training',
            'domain': "[('id', 'in', %s)]" % ids_list,
        }