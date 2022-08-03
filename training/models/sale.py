from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

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
                    if self.env['training'].search_count([('sale_id', '=', self.id)]) == 0 and self.env['training'].search_count([('sale_order_line_id', '=', line.id)]) == 0 :
                        vals = {'sale_id': self.id,
                                'sale_order_line_id': line.id,
                                'name': 'FORMATION',
                                'company_id': self.company_id.id,
                                'partner_id': self.partner_id.id}
                        self.env['training'].create(vals)

        return True
