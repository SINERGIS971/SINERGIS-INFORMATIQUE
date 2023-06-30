# -*- coding: utf-8 -*-
from odoo import http
import json
import re
import requests
from datetime import date

class HelpdeskFormController(http.Controller):
    @http.route('/help_sinergis', auth='public', methods=['GET'])
    def index_get(self, **kw):
        token = kw.get("token")
        csrf = http.request.csrf_token()
        return http.request.render("sinergis_helpdesk_form.form_page",{'csrf': csrf})
    
    @http.route('/help_sinergis', auth='public', methods=['POST'])
    def index_post(self, **kw):
        # Token for response
        recaptcha_response = kw.get("g-recaptcha-response")
        data = {}
        secret_server_key = "6Lf5wOMmAAAAAAHHM43V-jETpH-FEFM4l7nAlcmX" # Secret key
        client_ip = http.request.httprequest.remote_addr # Client IP address 
        data = {'secret': secret_server_key, 'response': recaptcha_response, 'remoteip': client_ip}
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data).content.decode('utf-8')
        response_dict = json.loads(response)
        if response_dict['success'] != "true":
            return "Erreur : Le recaptcha n'est pas validé."
        name = kw.get("name")
        company = kw.get("company")
        email = kw.get("email")
        product_select = kw.get("product-select")
        problem = kw.get("product-select")
        if not name or not company or not email or not product_select or not problem:
            return "Il vous manque des informations dans le formulaire que vous venez d'envoyer."
        return f"{name}, {company}, {email}, {product_select}, {problem}"
        

        
