# -*- coding: utf-8 -*-
from odoo import http


class SinergisCOntroller(http.Controller):
    @http.route('/sinergis/get_subproduct', auth='public', methods=['GET'])
    def index_get(self, **kw):
        if "product_id" in kw:
            product_id = int(kw.get('product_id'))
            subproduct_ids = http.request.env['sale.products.subproducts'].search([('product_id','=',product_id)])
            data = []
            for subproduct_id in subproduct_ids:
                data.append({
                    'id': subproduct_id.id,
                    'name': subproduct_id.name
                })
            return {'subproducts': data}
        return ""