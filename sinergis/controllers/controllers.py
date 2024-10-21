# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response

import json

class SinergisController(http.Controller):
    @http.route('/sinergis/get_subproduct', auth='public', methods=['GET'])
    def index_get(self, **kw):
        if "product_id" in kw:
            product_id = int(kw.get('product_id'))
            subproduct_ids = http.request.env['sale.products.subproducts'].sudo().search([('product_id','=',product_id),('label','!=',False)], order='order DESC')
            data = []
            for subproduct_id in subproduct_ids:
                data.append({
                    'id': subproduct_id.id,
                    'name': subproduct_id.label
                })
            headers_json = {'Content-Type': 'application/json'} 
            return Response(json.dumps({'subproducts': data}), headers=headers_json)
        return ""