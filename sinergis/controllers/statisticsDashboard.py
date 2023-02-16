from odoo import http
from odoo.http import request
from datetime import date

class StatisticsDashboard(http.Controller):
    @http.route('/sinergis/statistics_dashboard', auth='user', methods=['GET','POST'])
    def index (self, **kw):
        uid = request.uid
        #Add user group verification
        today = date.today()
        data = ""
        tasks = request.env["project.task"].search(['&amp;',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')])
        for task in tasks :
            data += task.name
            data += "<br/>"
        return data