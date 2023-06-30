# -*- coding: utf-8 -*-
from odoo import http
import re
from datetime import date

class Training(http.Controller):
    @http.route('/help_sinergis', auth='public', methods=['GET'])
    def index(self, **kw):
        token = kw.get("token")

        return http.request.render("sinergis_helpdesk_form.forme_page")

