# -*- coding: utf-8 -*-
from odoo import http
import json
import re
import requests
from datetime import date

class HelpdeskFormController(http.Controller):
    @http.route('/help_sinergis', auth='public', methods=['GET','POST'])
    def index(self, **kw):
        csrf = http.request.csrf_token()
        products = http.request.env['sale.products'].search([], limit=500)
        error = False
        success = False
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
            name = kw.get("name")
            company = kw.get("company")
            email = kw.get("email")
            product_select = int(kw.get("products"))
            subproduct_select = False
            if "subproducts" in kw:
                subproduct_select = int(kw.get("subproducts"))
            subject = kw.get("subject")
            problem = kw.get("problem")
            if not name or not company or not email or not product_select or not subject or not problem:
                error = "Il vous manque des informations dans le formulaire que vous venez d'envoyer."
            product_id = http.request.env['sale.products'].search([('id','=',product_select)],limit=1)
            if not product_id:
                error = "Le produit que vous venez de sélectionner n'existe pas dans notre base de données."
            if subproduct_select:
                subproduct_id = http.request.env['sale.products.subproducts'].search([('id','=',subproduct_select)],limit=1)
                if not subproduct_id:
                    error = "Le sous-produit que vous venez de sélectionner n'existe pas dans notre base de données."
            if not error :
                success = True
                data = {
                    'name': subject,
                    'description': problem,
                    'user_id': http.request.env.uid,
                    'team_id': http.request.env['helpdesk.ticket']._default_team_id(),
                    'x_sinergis_helpdesk_ticket_produits_new': product_select,
                    'x_sinergis_helpdesk_ticket_sous_produits_new': subproduct_select,
                }
                contact_id = http.request.env['res.partner'].search([('email','=',email),('is_company','=',False)],limit=1)
                if contact_id:
                    parent_id = contact_id.parent_id
                    if not parent_id:
                        data['partner_id'] = contact_id.id
                    else :
                        data['partner_id'] = contact_id.id
                        data['x_sinergis_helpdesk_ticket_contact'] = contact_id.id
                else:
                    contact_id = http.request.env['res.partner'].create({'name': name, 'email': email, 'is_company': False})
                    data['partner_id'] = contact_id.id
                    data['x_sinergis_helpdesk_ticket_contact'] = contact_id.id
                
                http.request.env['helpdesk.ticket'].create(data)

        return http.request.render("sinergis_helpdesk_form.form_page",{'csrf': csrf,'products': products, 'error': error, 'success': success})

        
