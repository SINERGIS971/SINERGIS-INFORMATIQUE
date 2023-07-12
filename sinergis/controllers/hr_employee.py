import zipfile
import base64

from io import BytesIO

from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

class HrEmployeeController(http.Controller):
    @http.route('/sinergis/download_cv', auth='user', methods=['GET'], csrf=False)
    def index (self, **kw):
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return False

        employee_ids = request.env['hr.employee'].search([])
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for employee_id in employee_ids:
                if employee_id.cv_file:
                    name_cv = f"CV/{employee_id.cv_filename}"
                    content_cv_base64 = employee_id.cv_file
                    content_cv = base64.b64decode(content_cv_base64)
                    zipf.writestr(name_cv, content_cv)

        return http.send_file(zip_buffer, filename='CV_ET_CERTIFICATS.zip', as_attachment=True)