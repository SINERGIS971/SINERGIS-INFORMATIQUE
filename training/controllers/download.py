from odoo import http
from odoo.http import request

# Télécharger le diagnostic inital depuis les ventes
class DownloadInitialeDiagnostique(http.Controller):
    @http.route(['/training/download_initiale_diagnostique'], type='http', auth="user", csrf=False)
    def download_initiale_diagnostique(self, **kw):
        response = request.make_response(
        None,
        headers=[
           ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
           ("Content-disposition", f"attachment;filename=diagnostic_initial.docx")
        ]
        )
        result = self.env['ir.config_parameter'].sudo().get_param('training.diagnostic_initial')
        response.stream.write(result)
        return response