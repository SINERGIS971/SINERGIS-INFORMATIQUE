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
        # User verification
        uid = request.uid
        user = request.env["res.users"].search([("id", "=", uid)])
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return "Vous n'êtes pas autorisé à accéder à cette page. Merci de vous rapporcher d'un administrateur."
        # Loading date parameter
        date_end = date.today()
        #if "hourly_contract_date" in kw :
        #    date_end = datetime.strptime(kw["hourly_contract_date"], '%Y-%m-%d').date()
        #Filtre pour tâches CH non archivées et archivées

        #Ancien système de calcul du nombres d'heures restantes. À retirer si aucun besoin d'Alain
        """
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
        """
        return http.request.render("sinergis.statistics_dashboard_page", {
                            "actual_year": date.today(),
                            #"date_end_text" : date_end.strftime("%A %d %B %Y"),
                            #"date_end" : date_end.strftime("%Y-%m-%d"),
                            #"total_hours" : total_hours,
                            #"total_hours_guadeloupe" : total_hours_guadeloupe,
                            #"total_hours_martinique" : total_hours_martinique,
                        })

class InvoiceExcelReportController(http.Controller):
    @http.route(['/sinergis/statistics_dashboard/hour_contract_excel'], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, **kw):
        # User verification
        uid = request.uid
        user = request.env["res.users"].search([("id", "=", uid)])
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return "Vous n'êtes pas autorisé à accéder à cette page. Merci de vous rapporcher d'un administrateur."
        #=========================
        #Paramètres de génération :
         #=========================
        if not "hour_contract_excel_begin_date" in kw or not "hour_contract_excel_end_date" in kw :
            return "Il manque la plage de date afin de générer le document, merci de contacter un administrateur système."
        begin_date = datetime.strptime(kw["hour_contract_excel_begin_date"], '%Y-%m-%d').date()
        end_date = datetime.strptime(kw["hour_contract_excel_end_date"], '%Y-%m-%d').date()
        #Companies à include dans excel
        allowed_companies = []
        if "sinergis_gpe_checkbox" in kw :
            allowed_companies.append("SINERGIS GPE")
        if "sinergis_mqe_checkbox" in kw :
            allowed_companies.append("SINERGIS MQE")
        if "sinergis_guy_checkbox" in kw :
            allowed_companies.append("SINERGIS GUY")
        if "sinergis_brd_checkbox" in kw :
            allowed_companies.append("SINERGIS BRD")
        #Chargement des données
        # En sortie de la fonction nous obtenons deux tableaux. Le premier pour les CH consommés à end_date
        # et le second pour les CH non consommés
        data_consumed, data_not_consumed = InvoiceExcelReportController.get_hour_contract_data(request, begin_date, end_date, allowed_companies)
        
        #=============================
        # Création du nom du fichier
        #=============================
        
        filename = f"CH-{begin_date.strftime('%d%m%Y')}-AU-{end_date.strftime('%d%m%Y')}"
        
        #=============================
        # Création de la réponse Http
        #=============================
        response = request.make_response(
        None,
        headers=[
           ('Content-Type', 'application/vnd.ms-excel'),
           ("Content-disposition", f"attachment;filename={filename}.xls")
        ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({'bold': True, 'font_color': 'blue'})
        red_text = workbook.add_format({'font_color': 'red'})
        green_text = workbook.add_format({'font_color': 'green'})

        #CH NON CONSOMMES
        sheet_1 = workbook.add_worksheet("CH NON CONSOMMES A 100%")
        sheet_1.set_column(0, 8, 30)
        sheet_1.set_column(6, 6, 50)

        sheet_1.write(0, 0, 'Date de création du contrat', header_format)
        sheet_1.write(0, 1, "Date d'expiration", header_format)
        sheet_1.write(0, 2, 'Bon de commande N°', header_format)
        sheet_1.write(0, 3, 'Contrat PME / MGE', header_format)
        sheet_1.write(0, 4, 'Client', header_format)
        sheet_1.write(0, 5, 'Heures prévues initialement', header_format)
        sheet_1.write(0, 6, f'Heures consommées entre le {begin_date.strftime("%d/%m/%Y")} et {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_1.write(0, 7, f'Heures restantes le {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_1.write(0, 8, 'Société', header_format)
        
        line = 1
        for data_line in data_not_consumed:
            sheet_1.write(line, 0, data_line["create_date"])
            sheet_1.write(line, 1, data_line["date_deadline"])
            sheet_1.write(line, 2, data_line["command_number"])
            sheet_1.write(line, 3, data_line["type"])
            sheet_1.write(line, 4, data_line["client"])
            sheet_1.write(line, 5, data_line["planned_hours"])
            sheet_1.write(line, 6, data_line["effective_hours"])
            sheet_1.write(line, 7, data_line["remaining_hours"],green_text)
            sheet_1.write(line, 8, data_line["company"])
            line += 1
        
        #CH CONSOMMES
        sheet_2 = workbook.add_worksheet("CH CONSOMMES")
        sheet_2.set_column(0, 9, 30)
        sheet_2.set_column(6, 6, 50)  # Pour la colonne heures passées qui est plus large
        
        sheet_2.write(0, 0, 'Date de création du contrat', header_format)
        sheet_2.write(0, 1, "Date d'expiration", header_format)
        sheet_2.write(0, 2, 'Bon de commande N°', header_format)
        sheet_2.write(0, 3, 'Contrat PME / MGE', header_format)
        sheet_2.write(0, 4, 'Client', header_format)
        sheet_2.write(0, 5, 'Heures prévues initialement', header_format)
        sheet_2.write(0, 6, f'Heures consommées entre le {begin_date.strftime("%d/%m/%Y")} et {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_2.write(0, 7, f'Heures restantes le {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_2.write(0, 8, 'Archivé à ce jour ?', header_format)
        sheet_2.write(0, 9, 'Société', header_format)
        
        line = 1
        for data_line in data_consumed:
            sheet_2.write(line, 0, data_line["create_date"])
            sheet_2.write(line, 1, data_line["date_deadline"])
            sheet_2.write(line, 2, data_line["command_number"])
            sheet_2.write(line, 3, data_line["type"])
            sheet_2.write(line, 4, data_line["client"])
            sheet_2.write(line, 5, data_line["planned_hours"])
            sheet_2.write(line, 6, data_line["effective_hours"])
            sheet_2.write(line, 7, data_line["remaining_hours"],red_text)
            if data_line["active"] :
                sheet_2.write(line, 7, "OUI",green_text)
            else:
                sheet_2.write(line, 7, "NON",red_text)
            sheet_2.write(line, 8, data_line["company"])
            line += 1
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    #Fonction de génération des contrats d'heures non consommés
    #Prend en entrée l'objet request d'odoo, la date de début du calcul et la date de fin
    def get_hour_contract_data (request, begin_date, end_date, allowed_companies):
        data_not_consumed = []
        data_consumed = []
        tasks = request.env["project.task"].search(['&','&','|',('active','=',False),('active','=',True),('create_date','<=',end_date.strftime("%Y-%m-%d")),'&',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')],order='create_date desc')
        
        for task in tasks :
            #Calcul de la deadline
            date_deadline = ""
            if task.date_deadline :
                date_deadline = task.date_deadline.strftime("%d/%m/%Y")
            # On détermine le pays du CH
            company = ""
            project_name = task.project_id.name
            if "GPE" in project_name :
                company = "SINERGIS GPE"
            elif "MQE" in project_name :
                company = "SINERGIS MQE"
            elif "GUY" in project_name :
                company = "SINERGIS GUY"
            elif "BRD" in project_name :
                company = "SINERGIS BRD"

            # On détermine si c'est un CH MGE 
            type = ""
            if "PME" in project_name:
                type = "PME"
            elif "MGE" in project_name:
                type = "MGE"
            
            # Calcul des heures restantes et heures réalisées
            remaining_hours = task.planned_hours # Heures restantes
            effective_hours = 0 # Heures réalisées
            # On soustrait ensuite chaque intervention avant la date demandée
            timesheet_ids = request.env["account.analytic.line"].search([('task_id', '=', task.id),('create_date','<=',end_date.strftime("%Y-%m-%d"))])
            for timesheet_id in timesheet_ids :
                remaining_hours -= timesheet_id.unit_amount
                if timesheet_id.date >= begin_date :
                    effective_hours += timesheet_id.unit_amount
            remaining_hours = round(remaining_hours, 1)
            effective_hours = round(effective_hours, 1)
            
            element = {
                "create_date" : task.create_date.strftime("%d/%m/%Y %H:%M:%S"),
                "date_deadline" : date_deadline, #COMPUTE
                "command_number" : task.sale_order_id.name,
                "type": type, #COMPUTE
                "client" : task.partner_id.name,
                "planned_hours" : task.planned_hours,
                "effective_hours" : effective_hours,#task.effective_hours,
                "remaining_hours" : remaining_hours, #COMPUTE
                "active" : task.active,
                "company" : company, #COMPUTE
                }
            
            # Si l'utilisateur a demandé les informations de cette companie
            if company in allowed_companies :
                #On regarde si à end_date, le contrat d'heure est consommé ou non
                if remaining_hours <= 0 :
                    data_consumed.append(element)
                else :
                    data_not_consumed.append(element)
            
        # Calcul des sous-totaux de chaque société Sinergis
        #data_consumed_subtotal = {}
        #for element in data_consumed :
        #    data_consumed_subtotal[element["company"]]['planneld_hours'] = 

        return data_consumed, data_not_consumed
    