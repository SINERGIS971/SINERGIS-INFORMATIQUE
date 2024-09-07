from odoo import http
from odoo.http import request
from datetime import date
from datetime import datetime

import io
import math
import pandas as pd
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
                            "actual_year": date.today().year,
                            "actual_month": date.today().month,
                            "actual_day": date.today().day,
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
        #=================================
        # Données de sommation des valeurs
        #=================================
        sum_data = {
            "planned_hours" :{
                "consumed" :{
                    "company" : 0,
                    "total" : 0
                },
                "not_consumed" :{
                    "company" : 0,
                    "total" : 0
                }
              },
            "effective_hours" :{
                "consumed" :{
                    "company" : 0,
                    "total" : 0
                },
                "not_consumed" :{
                    "company" : 0,
                    "total" : 0
                }
              },
            "remaining_hours" :{
                "consumed" :{
                    "company" : 0,
                    "total" : 0
                },
                "not_consumed" :{
                    "company" : 0,
                    "total" : 0
                }
              }
        }


        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({'bold': True, 'font_color': 'blue'})
        sum_format = workbook.add_format({'bg_color': "#CFCFCF", 'bold': True})
        red_text = workbook.add_format({'font_color': 'red'})
        green_text = workbook.add_format({'font_color': 'green'})

        #CH NON CONSOMMES
        sheet_1 = workbook.add_worksheet("CH NON CONSOMMES A 100%")
        sheet_1.set_column(0, 9, 30)
        sheet_1.set_column(7, 7, 50)

        sheet_1.write(0, 0, 'Date de création du contrat', header_format)
        sheet_1.write(0, 1, 'Crée par', header_format)
        sheet_1.write(0, 2, "Date d'expiration", header_format)
        sheet_1.write(0, 3, 'Bon de commande N°', header_format)
        sheet_1.write(0, 4, 'Contrat PME / MGE', header_format)
        sheet_1.write(0, 5, 'Client', header_format)
        sheet_1.write(0, 6, 'Heures prévues initialement', header_format)
        sheet_1.write(0, 7, f'Heures consommées entre le {begin_date.strftime("%d/%m/%Y")} et {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_1.write(0, 8, f'Heures restantes le {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_1.write(0, 9, 'Société', header_format)
        sheet_1.write(0, 10, 'Société', header_format)
        
        line = 1
        if data_not_consumed :
            last_data_line_company = data_not_consumed[0]["company"]
        for data_line in data_not_consumed:
            #Ligne somme des valeurs numériques de la société Sinergis
            if data_line["company"] != last_data_line_company:
                for i in range(0,10):
                    sheet_1.write(line, i, "", sum_format)
                sheet_1.write(line, 0, last_data_line_company, sum_format)
                sheet_1.write(line, 6, sum_data['planned_hours']['not_consumed']['company'], sum_format)
                sheet_1.write(line, 7, sum_data['effective_hours']['not_consumed']['company'], sum_format)
                sheet_1.write(line, 8, sum_data['remaining_hours']['not_consumed']['company'], sum_format)
                sum_data['planned_hours']['not_consumed']['company'] = 0
                sum_data['effective_hours']['not_consumed']['company'] = 0
                sum_data['remaining_hours']['not_consumed']['company'] = 0
                last_data_line_company = data_line["company"]
                line += 1

            # Ligne du CH
            sheet_1.write(line, 0, data_line["create_date"])
            sheet_1.write(line, 1, data_line["create_by"])
            sheet_1.write(line, 2, data_line["date_deadline"])
            sheet_1.write(line, 3, data_line["command_number"])
            sheet_1.write(line, 4, data_line["type"])
            sheet_1.write(line, 5, data_line["client"])
            sheet_1.write(line, 6, data_line["planned_hours"])
            sheet_1.write(line, 7, data_line["effective_hours"])
            sheet_1.write(line, 8, data_line["remaining_hours"],green_text)
            sheet_1.write(line, 9, data_line["company"])
            sheet_1.write(line, 10, data_line["dispute"])
            # Sum data treatment
            sum_data['planned_hours']['not_consumed']['total'] += float(data_line["planned_hours"])
            sum_data['effective_hours']['not_consumed']['total'] += float(data_line["effective_hours"])
            sum_data['remaining_hours']['not_consumed']['total'] += float(data_line["remaining_hours"])
            sum_data['planned_hours']['not_consumed']['company'] += float(data_line["planned_hours"])
            sum_data['effective_hours']['not_consumed']['company'] += float(data_line["effective_hours"])
            sum_data['remaining_hours']['not_consumed']['company'] += float(data_line["remaining_hours"])
            line += 1
        if data_not_consumed :
            # Ligne somme dernière société Sinergis
            for i in range(0,10):
                sheet_1.write(line, i, "", sum_format)
            sheet_1.write(line, 0, last_data_line_company, sum_format)
            sheet_1.write(line, 6, sum_data['planned_hours']['not_consumed']['company'], sum_format)
            sheet_1.write(line, 7, sum_data['effective_hours']['not_consumed']['company'], sum_format)
            sheet_1.write(line, 8, sum_data['remaining_hours']['not_consumed']['company'], sum_format)
            line += 1
            # Ligne finale total
            for i in range(0,10):
                sheet_1.write(line, i, "", sum_format)
            sheet_1.write(line, 0, "TOTAL", sum_format)
            sheet_1.write(line, 6, sum_data['planned_hours']['not_consumed']['total'], sum_format)
            sheet_1.write(line, 7, sum_data['effective_hours']['not_consumed']['total'], sum_format)
            sheet_1.write(line, 8, sum_data['remaining_hours']['not_consumed']['total'], sum_format)
        
        #CH CONSOMMES
        sheet_2 = workbook.add_worksheet("CH CONSOMMES")
        sheet_2.set_column(0, 11, 30)
        sheet_2.set_column(7, 7, 50)  # Pour la colonne heures passées qui est plus large
        
        sheet_2.write(0, 0, 'Date de création du contrat', header_format)
        sheet_2.write(0, 1, 'Crée par', header_format)
        sheet_2.write(0, 2, "Date d'expiration", header_format)
        sheet_2.write(0, 3, 'Bon de commande N°', header_format)
        sheet_2.write(0, 4, 'Contrat PME / MGE', header_format)
        sheet_2.write(0, 5, 'Client', header_format)
        sheet_2.write(0, 6, 'Heures prévues initialement', header_format)
        sheet_2.write(0, 7, f'Heures consommées entre le {begin_date.strftime("%d/%m/%Y")} et {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_2.write(0, 8, f'Heures restantes le {end_date.strftime("%d/%m/%Y")}', header_format)
        sheet_2.write(0, 9, 'Archivé à ce jour ?', header_format)
        sheet_2.write(0, 10, 'Autre contrat à ce jour ?', header_format)
        sheet_2.write(0, 11, 'Société', header_format)
        sheet_2.write(0, 12, 'Litige', header_format)
        
        line = 1
        if data_consumed :
            last_data_line_company = data_consumed[0]["company"]
        for data_line in data_consumed:
            #Ligne somme des valeurs numériques de la société Sinergis
            if data_line["company"] != last_data_line_company:
                for i in range(0,12):
                    sheet_2.write(line, i, "", sum_format)
                sheet_2.write(line, 0, last_data_line_company, sum_format)
                sheet_2.write(line, 6, sum_data['planned_hours']['consumed']['company'], sum_format)
                sheet_2.write(line, 7, sum_data['effective_hours']['consumed']['company'], sum_format)
                sheet_2.write(line, 8, sum_data['remaining_hours']['consumed']['company'], sum_format)
                sum_data['planned_hours']['consumed']['company'] = 0
                sum_data['effective_hours']['consumed']['company'] = 0
                sum_data['remaining_hours']['consumed']['company'] = 0
                last_data_line_company = data_line["company"]
                line += 1

            # Ligne du CH
            sheet_2.write(line, 0, data_line["create_date"])
            sheet_2.write(line, 1, data_line["create_by"])
            sheet_2.write(line, 2, data_line["date_deadline"])
            sheet_2.write(line, 3, data_line["command_number"])
            sheet_2.write(line, 4, data_line["type"])
            sheet_2.write(line, 5, data_line["client"])
            sheet_2.write(line, 6, data_line["planned_hours"])
            sheet_2.write(line, 7, data_line["effective_hours"])
            sheet_2.write(line, 8, data_line["remaining_hours"],red_text)
            if data_line["active"] :
                sheet_2.write(line, 9, "NON",red_text)
            else:
                sheet_2.write(line, 9, "OUI",green_text)
            if data_line["is_other_contract"] :
                sheet_2.write(line, 10, "OUI",green_text)
            else:
                sheet_2.write(line, 10, "NON",red_text)
            sheet_2.write(line, 11, data_line["company"])
            sheet_2.write(line, 12, data_line["dispute"])

            # Sum data treatment
            sum_data['planned_hours']['consumed']['total'] += float(data_line["planned_hours"])
            sum_data['effective_hours']['consumed']['total'] += float(data_line["effective_hours"])
            sum_data['remaining_hours']['consumed']['total'] += float(data_line["remaining_hours"])
            sum_data['planned_hours']['consumed']['company'] += float(data_line["planned_hours"])
            sum_data['effective_hours']['consumed']['company'] += float(data_line["effective_hours"])
            sum_data['remaining_hours']['consumed']['company'] += float(data_line["remaining_hours"])
            line += 1
        if data_consumed :
            # Ligne somme dernière société Sinergis
            for i in range(0,12):
                sheet_2.write(line, i, "", sum_format)
            sheet_2.write(line, 0, last_data_line_company, sum_format)
            sheet_2.write(line, 6, sum_data['planned_hours']['consumed']['company'], sum_format)
            sheet_2.write(line, 7, sum_data['effective_hours']['consumed']['company'], sum_format)
            sheet_2.write(line, 8, sum_data['remaining_hours']['consumed']['company'], sum_format)
            line += 1
            # Ligne finale total
            for i in range(0,12):
                sheet_2.write(line, i, "", sum_format)
            sheet_2.write(line, 0, "TOTAL", sum_format)
            sheet_2.write(line, 6, sum_data['planned_hours']['consumed']['total'], sum_format)
            sheet_2.write(line, 7, sum_data['effective_hours']['consumed']['total'], sum_format)
            sheet_2.write(line, 8, sum_data['remaining_hours']['consumed']['total'], sum_format)
        
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
        tasks = request.env["project.task"].search(['&','&','|',('active','=',False),('active','=',True),('create_date','<=',end_date.strftime("%Y-%m-%d")),'&',('project_id.name','ilike','HEURES'),('project_id.name','ilike','CONTRAT D')],order='company_id desc, create_date desc')
        
        for task in tasks :
            #Calcul de la deadline
            date_deadline = ""
            if task.date_deadline :
                date_deadline = task.date_deadline.strftime("%d/%m/%Y")

            # On détermine si c'est un CH MGE 
            project_name = task.project_id.name
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
            
            # On vérifie si le client n'a pas d'autre contrat à ce jour (pour les CH consommés)
            other_contract = request.env["project.task"].search(['&','&','&',('active','=',True),('remaining_hours','>','0'),('project_id.name','ilike',"CONTRAT D'HEURES"),('partner_id','=',task.partner_id.id)])
            if other_contract :
                is_other_contract = True
            else : 
                is_other_contract = False

            # On regarde les litiges du client
            dispute = "NON"
            dispute_douteux = task.partner_id.x_sinergis_societe_litige_douteux
            dispute_bloque = task.partner_id.x_sinergis_societe_litige_bloque
            if dispute_douteux and dispute_bloque:
                dispute = "Douteux et Bloqué"
            elif dispute_douteux:
                dispute = "Douteux"
            elif dispute_bloque:
                dispute="Bloqué"

            # Retrouver la commande dans tous les cas de figure
            sale_order_id = task.sale_order_id
            if not sale_order_id:
                sale_order_id = task.sale_line_id.order_id
            if not sale_order_id:
                sale_order_id = task.create_order_id

            element = {
                "create_date" : task.create_date.strftime("%d/%m/%Y %H:%M:%S"),
                "create_by" : sale_order_id.user_id.name,
                "date_deadline" : date_deadline, #COMPUTE
                "command_number" : sale_order_id.name,
                "type": type, #COMPUTE
                "client" : task.partner_id.name,
                "planned_hours" : task.planned_hours,
                "effective_hours" : effective_hours,#task.effective_hours,
                "remaining_hours" : remaining_hours, #COMPUTE
                "active" : task.active,
                "is_other_contract": is_other_contract,
                "company" : task.company_id.name,
                "dispute" : dispute
                }
            
            # Si l'utilisateur a demandé les informations de cette companie
            if task.company_id.name in allowed_companies :
                #On regarde si à end_date, le contrat d'heure est consommé ou non
                if remaining_hours <= 0 :
                    data_consumed.append(element)
                else :
                    data_not_consumed.append(element)

        return data_consumed, data_not_consumed
    
class TimeRecordingReportController(http.Controller):
    @http.route(['/sinergis/statistics_dashboard/time_recording_excel'], type='http', auth="user", csrf=False)
    def get_time_recording_excel_report(self, **kw):
        # User verification
        uid = request.uid
        user = request.env["res.users"].search([("id", "=", uid)])
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return "Vous n'êtes pas autorisé à accéder à cette page. Merci de vous rapporcher d'un administrateur."
        #=========================
        #Paramètres de génération :
        #=========================
        if not "time_recording_begin_date" in kw or not "time_recording_end_date" in kw :
            return "Il manque la plage de date afin de générer le document, merci de contacter un administrateur système."
        begin_date = datetime.strptime(kw["time_recording_begin_date"], '%Y-%m-%d').date()
        end_date = datetime.strptime(kw["time_recording_end_date"], '%Y-%m-%d').date()

        #=============================
        # Création du nom du fichier
        #=============================
        filename = f"SAISIE_TEMPS"

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

        #=============================
        # Création du document
        #=============================

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        title_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bg_color': '#adcdff', 'bold': True, 'font_color': 'blue'})
        sum_format = workbook.add_format({'bg_color': "#CFCFCF", 'bold': True})
        user_format = workbook.add_format({'bold': True})
        number_format = workbook.add_format()
        number_format.set_num_format('0.0')
        sum_format.set_num_format('0.0')

        # Écriture du titre de la page
        sheet_1 = workbook.add_worksheet("Saisie des temps")
        sheet_1.set_column(0, 8, 30)
        sheet_1.write(0, 0, f'Saisie des temps du {begin_date.strftime("%d/%m/%Y")} au {end_date.strftime("%d/%m/%Y")}', title_format)
        #sheet_1.conditional_format( 'A2:I2' , { 'type' : 'no_blanks' , 'format' : header_format})
        sheet_1.write(1, 0, '', header_format)
        sheet_1.write(1, 1, 'Facturable', header_format)
        sheet_1.write(1, 2, 'Non facturable', header_format)
        sheet_1.write(1, 3, 'Total', header_format)
        sheet_1.write(1, 4, 'Moyenne mensuelle', header_format)
        sheet_1.write(1, 5, 'Moyenne jour', header_format)
        sheet_1.write(1, 6, 'Moyenne mensuelle facturable', header_format)
        sheet_1.write(1, 7, 'Moyenne mensuelle non facturable', header_format)
        sheet_1.write(1, 8, 'Écart moyen mois / 169h', header_format)

        # Variable pour stocker le total de chaque colonne
        total_billable_time = 0
        total_not_billable_time = 0
        total_time = 0
        total_monthly_average = 0
        total_daily_average = 0
        total_monthly_billable_time_average = 0
        total_monthly_not_billable_time_average = 0

        # Calcul des champs par consultant
        consultant_ids = request.env['res.users'].search([('x_sinergis_res_users_job','=','CONSULTANT')])
        i = 3
        for consulant_id in consultant_ids:
            sheet_1.write(i, 0, consulant_id.name, user_format)
            action_ids = request.env["sinergis.myactions"].search([("consultant", "=", consulant_id.id), ('date','>=',begin_date.strftime("%Y-%m-%d 00:00:01")), ('date','<=',end_date.strftime("%Y-%m-%d 23:59:59"))])
            consultant_billable_sum = 0
            consultant_not_billable_sum = 0
            data = {
                'date': [],
                'billable_time': [],
                'not_billable_time': [],
                'total_time': []
            }
            for action_id in action_ids:
                action_date = action_id.date.strftime("%Y-%m-%d")
                if not action_date in data['date']:
                    data['date'].append(action_date)
                    data['billable_time'].append(0.0)
                    data['not_billable_time'].append(0.0)
                    data['total_time'].append(0.0)
                data_index = data['date'].index(action_date)
                data['total_time'][data_index] += action_id.time
                if action_id.billing_type == "Facturable":
                    consultant_billable_sum += action_id.time
                    data['billable_time'][data_index] += action_id.time
                elif action_id.billing_type == "Non facturable":
                    consultant_not_billable_sum += action_id.time
                    data['not_billable_time'][data_index] += action_id.time
            sum_billable_time = sum(data["billable_time"])
            sum_not_billable_time = sum(data["not_billable_time"])
            sum_total_time = sum(data["total_time"])
            total_billable_time += sum_billable_time
            total_not_billable_time += sum_not_billable_time
            total_time += sum_total_time
            sheet_1.write(i, 1, sum_billable_time, number_format)
            sheet_1.write(i, 2, sum_not_billable_time, number_format)
            sheet_1.write(i, 3, sum_total_time, number_format)

            # Utilisation de pandas pour extraction
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            monthly_average = df.groupby(df['date'].dt.to_period('M'))['total_time'].sum().mean()
            if math.isnan(monthly_average):
                monthly_average=0
            daily_average = 0
            if len(data['total_time']) > 0:
                daily_average = sum(data['total_time'])/len(data['total_time'])
            monthly_billable_time_average = df.groupby(df['date'].dt.to_period('M'))['billable_time'].sum().mean()
            monthly_not_billable_time_average = df.groupby(df['date'].dt.to_period('M'))['not_billable_time'].sum().mean()
            if math.isnan(monthly_billable_time_average):
                monthly_billable_time_average=0
            if math.isnan(monthly_not_billable_time_average):
                monthly_not_billable_time_average=0
            total_monthly_average += monthly_average
            total_daily_average += daily_average
            total_monthly_billable_time_average += monthly_billable_time_average
            total_monthly_not_billable_time_average += monthly_not_billable_time_average
            
            sheet_1.write(i, 4, monthly_average, number_format)
            sheet_1.write(i, 5, daily_average, number_format)
            sheet_1.write(i, 6, monthly_billable_time_average, number_format)
            sheet_1.write(i, 7, monthly_not_billable_time_average, number_format)
            sheet_1.write(i, 8, monthly_average-169, number_format) # Ecart / 169h
            i += 1

        # Affichage du total pour chaque colonne
        sheet_1.write(2, 0, 'Total', sum_format)
        sheet_1.write(2, 1, total_billable_time, sum_format)
        sheet_1.write(2, 2, total_not_billable_time, sum_format)
        sheet_1.write(2, 3, total_time, sum_format)
        sheet_1.write(2, 4, total_monthly_average, sum_format)
        sheet_1.write(2, 5, total_daily_average, sum_format)
        sheet_1.write(2, 6, total_monthly_billable_time_average, sum_format)
        sheet_1.write(2, 7, total_monthly_not_billable_time_average, sum_format)

        #=============================
        # Envoie du document
        #=============================

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response




# Fonctionnalité non implantée dans Odoo à ce jour, utilisée uniquement pour une extraction
class ArticlesReportController(http.Controller):
    @http.route(['/sinergis/statistics_dashboard/articles_report'], type='http', auth="user", csrf=False)
    def get_articles_report(self, **kw):
        # User verification
        uid = request.uid
        user = request.env["res.users"].search([("id", "=", uid)])
        if request.env.user.has_group('sinergis.group_statistics_dashboard') == False:
            return "Vous n'êtes pas autorisé à accéder à cette page. Merci de vous rapporcher d'un administrateur."
        #begin_date = datetime.strptime("2001-01-01", '%Y-%m-%d').date()
        end_date = datetime.strptime("2023-03-31", '%Y-%m-%d').date()
        
        #=============================
        # Création du nom du fichier
        #=============================
        
        filename = f"Analyse articles"
        
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
        sum_format = workbook.add_format({'bg_color': "#CFCFCF", 'bold': True})
        red_text = workbook.add_format({'font_color': 'red'})
        green_text = workbook.add_format({'font_color': 'green'})

        sheet_1 = workbook.add_worksheet("Page")
        sheet_1.set_column(0, 6, 30)
        

        sheet_1.write(0, 0, '', header_format)
        sheet_1.write(0, 1, 'Montant HT (€)', header_format)
        sheet_1.write(0, 2, "Montant TTC (€)", header_format)
        sheet_1.write(0, 3, "Marge (€)", header_format)
        sheet_1.write(0, 4, 'Heures planifiées', header_format)
        sheet_1.write(0, 5, 'Heures consommées', header_format)
        sheet_1.write(0, 6, 'Heures restantes', header_format)
        
        articles = request.env["product.product"].search([],order='name asc')
        i = 1
        _temp = []
        sum_price_subtotal = 0
        sum_price_total = 0
        sum_margin = 0
        sum_planned_hours = 0
        sum_effective_hours = 0
        for article in articles :
            sheet_1.write(i, 0, article.name, header_format)
            # PRICE TOTAL AND SUBTOTAL
            price_subtotal = 0
            price_total = 0
            margin = 0
            planned_hours = 0
            effective_hours = 0
            lines = request.env["sale.order.line"].search([('product_id', '=', article.id)])
            for line in lines :
                if line.order_id.state == "sale" and line.order_id.date_order.date() <= end_date:
                    price_subtotal += line.price_subtotal
                    price_total += line.price_total
                    margin += line.margin
                    # PLANNED HOURS
                    tasks = request.env["project.task"].search(['&',('sale_line_id', '=', line.id),'|',('active', '=', False),('active', '=', True)])
                    for task in tasks :
                        if not task.id in _temp:
                            _temp.append(task.id)
                            planned_hours += task.planned_hours
                            # EFFECTIVE HOURS
                            timesheets = request.env["account.analytic.line"].search([('task_id', '=', task.id),('create_date','<=',end_date.strftime("%Y-%m-%d"))])
                            for timesheet in timesheets:
                                effective_hours += timesheet.unit_amount
            sheet_1.write(i, 1, str(price_subtotal))
            sheet_1.write(i, 2, str(price_total))
            sheet_1.write(i, 3, str(margin))
            sheet_1.write(i, 4, str(planned_hours))
            sheet_1.write(i, 5, str(effective_hours))
            sheet_1.write(i, 6, str(planned_hours-effective_hours))
            sum_price_subtotal += price_subtotal
            sum_price_total += price_total
            sum_margin += margin
            sum_planned_hours += planned_hours
            sum_effective_hours += effective_hours
            i+=1
        sheet_1.write(i, 0, 'TOTAL', sum_format)
        sheet_1.write(i, 1, str(sum_price_subtotal), sum_format)
        sheet_1.write(i, 2, str(sum_price_total), sum_format)
        sheet_1.write(i, 3, str(sum_margin), sum_format)
        sheet_1.write(i, 4, str(sum_planned_hours), sum_format)
        sheet_1.write(i, 5, str(sum_effective_hours), sum_format)
        sheet_1.write(i, 6, str(sum_planned_hours-sum_effective_hours), sum_format)

            
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response