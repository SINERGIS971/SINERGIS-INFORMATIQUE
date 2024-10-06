# -*- coding: utf-8 -*-
from odoo import http
import base64
import html
import json
import re
import requests
import sys
from datetime import date

class HelpdeskFormController(http.Controller):
    @http.route('/help_sinergis', auth='public', methods=['GET','POST'])
    def index(self, **kw):
        csrf = http.request.csrf_token()
        products = http.request.env['sale.products'].sudo().search([], limit=500)
        error = False
        success = False
        extension_ids = http.request.env["sinergis_helpdesk_form.extension"].sudo().search([], limit=100)
        extensions = [extension_id.extension for extension_id in extension_ids]
        if http.request.httprequest.method == 'POST':
            # Token for response
            recaptcha_response = kw.get("g-recaptcha-response")
            data = {}
            secret_server_key = "6Lf5wOMmAAAAAAHHM43V-jETpH-FEFM4l7nAlcmX" # Secret key
            client_ip = http.request.httprequest.remote_addr # Client IP address 
            data = {'secret': secret_server_key, 'response': recaptcha_response, 'remoteip': client_ip}
            response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data).content.decode('utf-8')
            response_dict = json.loads(response)
            if response_dict['success'] != True:
                error = "Le recaptcha n'est pas validé."
            firstname = kw.get("firstname")
            lastname = kw.get("lastname")
            company = html.escape(kw.get("company"))
            code = kw.get("code")
            email = kw.get("email").lower()
            phone = html.escape(kw.get("phone"))
            product_select = int(kw.get("products"))
            subproduct_select = kw.get("subproducts")
            subject = kw.get("subject")
            problem = kw.get("problem")
            files = http.request.httprequest.files.getlist('files[]')
            # Verification des extensions
            # extensions = {".jpg", ".png", ".gif", ".jpeg",".pdf"}
            max_size = 10485760 # Taille maximale en bytes
            if not firstname or not lastname or not company or not code or not email or not phone or not phone or not product_select or not subject or not problem:
                error = "Il vous manque des informations dans le formulaire que vous venez d'envoyer."
            partner_id = http.request.env['res.partner'].sudo().search([('x_sinergis_societe_helpdesk_code', '=', code)], limit=1)
            if len(partner_id) == 0:
                error = "Le code client Sinergis est incorrect."
            product_id = http.request.env['sale.products'].sudo().search([('id','=',product_select)],limit=1)
            if not product_id:
                error = "Le produit que vous venez de sélectionner n'existe pas dans notre base de données."
            if subproduct_select:
                subproduct_id = http.request.env['sale.products.subproducts'].sudo().search([('id','=',subproduct_select)],limit=1)
                if not subproduct_id:
                    error = "Le sous-produit que vous venez de sélectionner n'existe pas dans notre base de données."
            if not error :
                success = True
                description = f"""
                    <body>
                    <strong>Nom et Prénom :</strong> {lastname} {firstname}<br/>
                    <strong>Société :</strong> {company}<br/>
                    <strong>Email :</strong> {email}<br/>
                    <strong>Téléphone :</strong> {phone}<br/>
                    <strong>Sujet :</strong> {subject}<br/>
                    <strong>Description :</strong><br/>
                    {problem}
                    </body>
                """
                data = {
                    'name': f"{company} : {subject}",
                    'description': description,
                    'user_id': False,
                    'partner_id': partner_id.id,
                    'team_id': http.request.env['helpdesk.ticket'].sudo()._default_team_id(),
                    'x_sinergis_helpdesk_ticket_produits_new': product_select,
                    'x_sinergis_helpdesk_ticket_sous_produits_new': subproduct_select,
                }

                # Recherche d'un contact dans la société associée au code client.
                contact_id = http.request.env['res.partner'].sudo().search([('email','=',email),('is_company','=',False),('parent_id','=',partner_id.id)],limit=1)
                data['x_sinergis_helpdesk_ticket_contact'] = contact_id.id

                # ANCIEN CODE
                # Check in contact without company
                #if not contact_id:
                #    contact_id = http.request.env['res.partner'].sudo().search([('email','=',email),('is_company','=',False)],limit=1)
                # Create a contact
                #if not contact_id :
                #    contact_id = http.request.env['res.partner'].sudo().create({'name': name, 'email': email, 'is_company': False})
                #parent_id = contact_id.parent_id
                #if parent_id:
                #    data['partner_id'] = parent_id.id
                #    data['x_sinergis_helpdesk_ticket_contact'] = contact_id.id
                #else:
                #    data['partner_id'] = contact_id.id
                #    data['x_sinergis_helpdesk_ticket_contact'] = contact_id.id
                
                
                ticket = http.request.env['helpdesk.ticket'].sudo().create(data)

                # Création des PJ associées au ticket
                attachement_ids = []
                for file in files :
                    name = file.filename
                    attached_file = file.read()
                    # Vérification de la taille et de l'extension
                    if sys.getsizeof(attached_file) < max_size and any(file.filename.endswith(ext) for ext in extensions):
                        attachement_id = http.request.env['ir.attachment'].sudo().create({
                            'name': name,
                            'res_model': 'helpdesk.ticket',
                            'res_id': ticket.id,
                            'type': 'binary',
                            'store_fname': file.filename,
                            'datas': base64.b64encode(attached_file),
                        })
                        attachement_ids.append(attachement_id.id)
                if len(attachement_ids) > 0:
                    ticket.message_post(
                        body="Le client à joint à sa demande un ou plusieurs fichiers.",
                        attachments=attachement_ids
                    )
        return http.request.render("sinergis_helpdesk_form.form_page",{'csrf': csrf,'products': products, 'error': error, 'success': success, 'extensions': extensions})

        
