from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID, Command

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # Permet de ne plus recevoir de mails à chaque fois qu'on est assigné à une page
    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        fnames = []
        field = self._fields.get('user_id')
        user_id = updated_values.get('user_id')
        if field and user_id and field.comodel_name == 'res.users' and (getattr(field, 'track_visibility', False) or getattr(field, 'tracking', False)):
            user = self.env['res.users'].sudo().browse(user_id)
            try:
                if user.active:
                    return [(user.partner_id.id, default_subtype_ids,False)] # Pas de template utilisé pour l'envoi de mail
            except:
                pass
        return []
    