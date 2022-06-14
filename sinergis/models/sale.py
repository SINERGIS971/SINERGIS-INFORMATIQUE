from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_sinergis_sale_order_objet = fields.Char(string="Objet")
    x_sinergis_sale_order_contact = fields.Many2one("res.partner",string="Contact", required="True")

    #METTRE LES CONDITIONS DE PAIEMENT PAR DEFAUT - OVERRIDE FONCTION DE BASE
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",default=lambda self: self.env['account.payment.term'].search([('name','=',"100% des logiciels et des contrats d'heures et 50% des prestations et formations. Le solde à livraison. à la commande")]))
    
