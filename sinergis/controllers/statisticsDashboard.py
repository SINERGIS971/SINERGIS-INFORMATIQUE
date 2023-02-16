from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

import locale
locale.setlocale(locale.LC_TIME,'')

class StatisticsDashboard(http.Controller):
    @http.route('/sinergis/statistics_dashboard', auth='user', methods=['GET','POST'], csrf=False)
    def index (self, **kw):
        uid = request.uid
        #Add user group verification
        date_end = date.today()
        if "hourly_contract_date" in kw :
            date_end = datetime.strptime(kw["hourly_contract_date"], '%Y-%m-%d').date()
        #Filtre pour tâches CH non archivées et archivées

        total_hours = 0

        tasks = request.env["project.task"].search(['&','&','|',('active','=',False),('active','=',True),('create_date','<=',date_end.strftime("%Y-%m-%d")),'&',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')])
        for task in tasks :
            #Par on fixe le nombre d'heures au temps prévu par le CH
            task_hours = task.planned_hours
            # On soustrait ensuite chaque intervention avant la date demandée
            timesheet_ids = request.env["account.analytic.line"].search([('task_id', '=', task.id),('create_date','<=',date_end.strftime("%Y-%m-%d"))])
            for timesheet_id in timesheet_ids :
                task_hours -= timesheet_id.unit_amount
            #Mettre le CH à 0 si il a un nombre d'heures restantes négative
            if task_hours < 0 :
                task_hours = 0
            total_hours += task_hours
            total_hours = round(total_hours, 2)
        return http.request.render("sinergis.statistics_dashboard_page", {
                            "date_end_text" : date_end.strftime("%A %d %B %Y"),
                            "date_end" : date_end.strftime("%Y-%m-%d"),
                            "total_hours" : total_hours,
                        })