from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    training_count = fields.Integer(compute="_compute_training_count")

    def download_initiale_diagnostique(self):
        result = self.env['ir.config_parameter'].sudo().get_param('training.diagnostic_initial')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': "Diagnostic_Initial", 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        #Training Module
        if self.state == "sale":
            for line in self.order_line:
                if line.product_id.is_training:
                    #Verify if the training does not exists
                    if self.env['training'].search_count(['&',('sale_id', '=', self.id),('sale_order_line_id', '=', line.id)]) == 0:
                        vals = {'sale_id': self.id,
                                'sale_order_line_id': line.id,
                                'name': line.name, #Formation name equal to the description of the order line
                                'company_id': self.company_id.id,
                                'partner_id': self.partner_id.id,
                                'duration': line.product_uom_qty}
                        self.env['training'].sudo().create(vals)

        return True

    #ACCES AUX FORMATIONS LIES AU DEVIS
    def action_view_training(self):
        training_ids = self.env["training"].sudo().search([("sale_id", "=", self.id)])
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

    @api.depends("training_count")
    def _compute_training_count(self):
        for rec in self:
            rec.training_count = self.env['training'].search_count([('sale_id', '=', rec.id)])