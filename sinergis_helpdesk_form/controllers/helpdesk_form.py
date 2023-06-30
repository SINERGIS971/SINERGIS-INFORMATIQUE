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
        recaptcha_response = kw.get("g-recaptcha-response")
        data = {}
        secret_server_key = "6Lf5wOMmAAAAAAHHM43V-jETpH-FEFM4l7nAlcmX"
        client_ip = http.request.httprequest.remote_addr
        data = {'secret': secret_server_key, 'response': recaptcha_response, 'remoteip': client_ip}
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data).content.decode('utf-8')
        response_dict = json.loads(response)
        return response_dict['success']
        return str(response)

