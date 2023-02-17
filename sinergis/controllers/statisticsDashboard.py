from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

import io
import xlsxwriter

import locale
locale.setlocale(locale.LC_ALL,'fr_FR.UTF-8')

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
        total_hours_guadeloupe = 0
        total_hours_martinique = 0

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
            #On regarde le pays du contrat d'heure
            project_name = task.project_id.name
            if "GPE" in project_name :
                total_hours_guadeloupe += task_hours
            elif "MQE" in project_name :
                total_hours_martinique += task_hours

            total_hours = round(total_hours, 2)
            total_hours_guadeloupe = round(total_hours_guadeloupe, 2)
            total_hours_martinique = round(total_hours_martinique, 2)
        return http.request.render("sinergis.statistics_dashboard_page", {
                            "date_end_text" : date_end.strftime("%A %d %B %Y"),
                            "date_end" : date_end.strftime("%Y-%m-%d"),
                            "total_hours" : total_hours,
                            "total_hours_guadeloupe" : total_hours_guadeloupe,
                            "total_hours_martinique" : total_hours_martinique,
                        })

class InvoiceExcelReportController(http.Controller):
    @http.route(['/excel'], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, report_id=None, **args):
        response = request.make_response(
        None,
        headers=[
           ('Content-Type', 'application/vnd.ms-excel'),
            #('Content-Disposition', 'Invoice_report' + '.xlsx')
           ("Content-disposition", "attachment;filename=myExcel.xls")
        ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({'bold': True, 'font_color': 'blue'})
        # prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("CH NON CONSOMMES A 100%")
        sheet.set_column(0, 7, 30)

        sheet.write(0, 0, 'Date de création du contrat', header_format)
        sheet.write(0, 1, "Date d'expiration", header_format)
        sheet.write(0, 2, 'Bon de commande N°', header_format)
        sheet.write(0, 3, 'Client', header_format)
        sheet.write(0, 4, 'Heures prévues initialement', header_format)
        sheet.write(0, 5, 'Heures passés entre le 01/01/2022 et 31/12/2022', header_format)
        sheet.write(0, 6, 'Heures restantes le 31/12/2022', header_format)
        sheet.write(0, 7, 'Société', header_format)
       
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response