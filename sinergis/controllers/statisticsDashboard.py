from odoo import http
from odoo.http import request

class StatisticsDashboard(http.Controller):
    @http.route('/sinergis/statistics_dashboard', auth='user', methods=['GET','POST'])
    def index (self, **kw):
        return request.session.uid