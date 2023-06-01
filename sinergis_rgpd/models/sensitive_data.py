from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta

class SinergisSensitiveData(models.Model):
    _name = "sinergis_rgpd.sensitive_data"
    _description = "Données sensibles Sinergis"
    _inherit = ["mail.thread","mail.activity.mixin"]

    is_create = fields.Boolean(default=False)
    active = fields.Boolean(string='Active', default=True)

    partner_id = fields.Many2one("res.partner", string="Société", required=True)
    user_id = fields.Many2one("res.users", string="Utilisateur",default=lambda self: self.env.user, required=True, readonly=True)
    name = fields.Char(string='Reference', required=True)
    file_path = fields.Char(string="Chemin du fichier", required=True)
    comment = fields.Text(string="Commentaire")
    deletion_date = fields.Datetime(string="Date de suppression",default=lambda self: datetime.now() + timedelta(days=30), required=True)
    archive_date = fields.Datetime(string="Date d'archivage",readonly=True)

    def action_document_is_removed (self):
        self.archive_date = datetime.now()
        self.active = False

    def is_sensitive_data_to_remove(self):
        data = self.env["sinergis_rgpd.sensitive_data"].search(['&','&',("active","=",True),("archive_date",">=",datetime.now().strftime('%Y-%m-%d 00:00:00')),("user_id","=",self.env.user.id)])
        if len(data) > 0 :
            return True
        else :
            return False

    #Lors de la création de ticket via mail, ajouter automatiquement le contact et la société attribuée
    @api.model_create_multi
    def create(self, list_vals):
        objects = super(SinergisSensitiveData, self).create(list_vals)
        for object in objects:
            object.activity_schedule('sinergis_rgpd.activity_sensitive_data',summary='Supprimer une donnée sensible',note="Supprimer une donnée sensible",date_deadline=object.deletion_date,user_id=object.user_id.id)
            object.is_create = True
        return objects