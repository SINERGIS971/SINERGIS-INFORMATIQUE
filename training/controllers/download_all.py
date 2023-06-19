import zipfile
import base64
from io import BytesIO

from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

class DownloadAllTraining(http.Controller):
    @http.route('/training/download_all', auth='user', methods=['GET','POST'], csrf=False)
    def index (self, **kw):
        if not "training_id" in kw :
            return "Aucune formation n'est sélectionnée."
        training_id = int(kw['training_id'])
        training = self.env['training'].search([('id', "=", training_id)], limit=1)
        if not training :
            return "La formation n'existe pas."
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            name_1 = "Fichier1.pdf"
            content_1_base64 = ""
            content_1 = base64.b64decode(content_1_base64)
            zipf.writestr(name_1, content_1)
        zip_content_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
        return zip_content_base64