from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_sinergis_sale_order_client_bloque = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_bloque")
    x_sinergis_sale_order_client_douteux = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_douteux")
    x_sinergis_sale_order_client_suspect = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_suspect")

    x_sinergis_sale_order_objet = fields.Char(string="Objet")
    x_sinergis_sale_order_contact = fields.Many2one("res.partner",string="Contact", required="True")

    @api.depends('x_sinergis_sale_order_client_bloque')
    def _compute_x_sinergis_sale_order_client_bloque (self):
        if self.partner_id:
            self.x_sinergis_sale_order_client_bloque = self.partner_id.x_sinergis_societe_litige_bloque
        else:
            self.x_sinergis_sale_order_client_bloque = False

    @api.depends('x_sinergis_sale_order_client_douteux')
    def _compute_x_sinergis_sale_order_client_douteux (self):
        if self.partner_id:
            self.x_sinergis_sale_order_client_douteux = self.partner_id.x_sinergis_societe_litige_douteux
        else:
            self.x_sinergis_sale_order_client_douteux = False

    @api.depends('x_sinergis_sale_order_client_suspect')
    def _compute_x_sinergis_sale_order_client_suspect (self):
        if self.partner_id:
            self.x_sinergis_sale_order_client_suspect = self.partner_id.x_sinergis_societe_suspect
        else:
            self.x_sinergis_sale_order_client_suspect = False

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        SaleOrder._compute_x_sinergis_sale_order_client_bloque(self)
        SaleOrder._compute_x_sinergis_sale_order_client_douteux(self)
        SaleOrder._compute_x_sinergis_sale_order_client_suspect(self)

    #METTRE LES CONDITIONS DE PAIEMENT PAR DEFAUT - OVERRIDE FONCTION DE BASE
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",default=lambda self: self.env['account.payment.term'].search([('name','=',"100% des logiciels et des contrats d'heures et 50% des prestations et formations. Le solde à livraison. à la commande")]))
