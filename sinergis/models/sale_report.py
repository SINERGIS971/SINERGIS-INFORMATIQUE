from odoo import tools
from odoo import api, fields, models

# ANALYSE DES VENTES

class SinergisSaleReport(models.Model):
    _name = "sinergis.sale.report"
    _description = "Sinergis Sales Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Référence de vente', readonly=True)
    date = fields.Datetime('Date de vente', readonly=True)
    product_id = fields.Many2one('product.product', 'Produit', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unité de mesure', readonly=True)
    product_uom_qty = fields.Float('Qté commandée', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Client', readonly=True)
    company_id = fields.Many2one('res.company', 'Société', readonly=True)
    user_id = fields.Many2one('res.users', 'Vendeur', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Total HT', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    margin = fields.Float('Margin')
    
    order_id = fields.Many2one('sale.order', 'Vente', readonly=True)

    def _select_sale(self, fields=None):
        if not fields:
            fields = {}
        select_ = """
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            s.id as order_id,
            SUM(l.margin / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS margin
        """
        for field in fields.values():
            select_ += field
        return select_

    def _from_sale(self, from_clause=''):
        from_ = """
                sale_order_line l
                      right outer join sale_order s on (s.id=l.order_id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause
        return from_

    def _group_by_sale(self, groupby=''):
        groupby_ = """
            l.product_id,
            l.order_id,
            t.uom_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.user_id,
            s.state,
            s.company_id,
            s.id %s
        """ % (groupby)
        return groupby_

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        if not fields:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        return '%s (SELECT %s FROM %s WHERE l.display_type IS NULL GROUP BY %s)' % \
               (with_, self._select_sale(fields), self._from_sale(from_clause), self._group_by_sale(groupby))

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))