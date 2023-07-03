# -*- coding: utf-8 -*-
from odoo import http
import json
import re
import requests
from datetime import date

class HelpdeskFormController(http.Controller):
    @http.route('/help_sinergis', auth='public', methods=['GET','POST'])
    def index_get(self, **kw):
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
                error = "Erreur : Le recaptcha n'est pas validé."
            name = kw.get("name")
            company = kw.get("company")
            email = kw.get("email")
            product_select = kw.get("products")
            problem = kw.get("problem")
            if not name or not company or not email or not product_select or not problem:
                error = "Il vous manque des informations dans le formulaire que vous venez d'envoyer."
            success = True

        xreturn http.request.render("sinergis_helpdesk_form.form_page",{'csrf': csrf,'products': products, 'error': error, 'success': success})

        
