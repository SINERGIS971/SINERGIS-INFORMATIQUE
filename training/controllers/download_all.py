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
        training = http.request.env['training'].search([('id', "=", training_id)], limit=1)
        if not training :
            return "La formation n'existe pas."
        # Création du nom du dossier
        folder_name = training.name if training.name else "DOSSIER FORMATION"           
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Ajout du devis signé
            if training.signed_quote:
                name_quote = f"{folder_name}/Devis_signé.pdf"
                content_quote_base64 = training.signed_quote
                content_quote = base64.b64decode(content_quote_base64)
                zipf.writestr(name_quote, content_quote)
            # Ajout du diagnostic initial
            if training.diagnosis_file:
                name_diagnosis = f"{folder_name}/Document_Diagnostic_Initial.pdf"
                content_diagnosis_base64 = training.diagnosis_file
                content_diagnosis = base64.b64decode(content_diagnosis_base64)
                zipf.writestr(name_diagnosis, content_diagnosis)
            # Ajout du document OPCO
            if training.opco_file:
                name_opco = f"{folder_name}/Document_OPCO.pdf"
                content_opco_base64 = training.opco_file
                content_opco = base64.b64decode(content_opco_base64)
                zipf.writestr(name_opco, content_opco)
            # Ajout de la convention de formation signée
            if training.signed_agreement:
                name_agreement = f"{folder_name}/Document_Convention_Formation_signée.pdf"
                content_agreement_base64 = training.signed_agreement
                content_agreement = base64.b64decode(content_agreement_base64)
                zipf.writestr(name_agreement, content_agreement)

            # Génération du document récapitulatif du quiz
            name_quiz = f"{folder_name}/Document_Quiz.pdf"
            content_quiz = http.request.env.ref('training.training_quiz_report')._render_qweb_pdf(training.ids)[0]
            zipf.writestr(name_quiz, content_quiz)

            # Génération du document d'évaluation de la formation
            if training.evaluating_training_course:
                name_evaluation = f"{folder_name}/Document_Evaluation.pdf"
                content_evaluation = http.request.env.ref('training.training_consultant_evaluation_report')._render_qweb_pdf(training.ids)[0]
                zipf.writestr(name_evaluation, content_evaluation)

            # Ajout des feuilles d'émargement
            if len(training.signed_attendance_sheets) > 0:
                i = 1
                for sheet in training.signed_attendance_sheets:
                    name_attendance_sheet = f"{folder_name}/FEUILLES EMARGEMENT/Document_Feuille_Emargement_{str(i)}.pdf"
                    content_attendance_sheet_base64 = sheet.file
                    content_attendance_sheet = base64.b64decode(content_attendance_sheet_base64)
                    zipf.writestr(name_attendance_sheet, content_attendance_sheet)

        data = BytesIO(base64.standard_b64decode(zip_buffer.getvalue()))
        return http.send_file(zip_buffer, filename='archive12.zip', as_attachment=True)