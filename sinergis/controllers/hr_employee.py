import zipfile
import base64

from io import BytesIO

from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

class HrEmployeeController(http.Controller):
    @http.route('/sinergis/download_cv_certification', auth='user', methods=['GET'], csrf=False)
    def index (self, **kw):
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return False
        employee_ids = request.env['hr.employee'].search([])
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for employee_id in employee_ids:
                if employee_id.cv_file:
                    name_cv = f"{employee_id.name}/CV.pdf"
                    content_cv_base64 = employee_id.cv_file
                    content_cv = base64.b64decode(content_cv_base64)
                    zipf.writestr(name_cv, content_cv)
                certification_ids = request.env['hr.employee.certification'].search([('employee_id','=',employee_id.id)])
                for certification_id in certification_ids:
                    name_certification = f"{employee_id.name}/CERTIFICATIONS/{certification_id.filename}"
                    content_certification_base64 = certification_id.file
                    content_certification = base64.b64decode(content_certification_base64)
                    zipf.writestr(name_certification, content_certification)

        return http.send_file(zip_buffer, filename='CV_ET_CERTIFICATS.zip', as_attachment=True)