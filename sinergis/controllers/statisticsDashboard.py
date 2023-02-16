from odoo import http
from odoo.http import request
from datetime import date

class StatisticsDashboard(http.Controller):
    @http.route('/sinergis/statistics_dashboard', auth='user', methods=['GET','POST'])
    def index (self, **kw):
        uid = request.uid

        #DEBUG
        #Add user group verification
        today = date.today()
        data = ""
        #Filtre pour tâches CH non archivées et archivées
        n = 0
        #END DEBUG

        total_time = 0

        tasks = request.env["project.task"].search(['|','&','&',('active','=',False),('active','=',True),('create_date','<=','2023-02-16'),'&',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')])
        for task in tasks :
            planned_hours = task.planned_hours
            timesheet_ids = task.timesheet_ids
            data += task.name
            data += "<br/>"
            n+=1
        data+=str(n)