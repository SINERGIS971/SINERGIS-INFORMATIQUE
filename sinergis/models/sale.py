from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_sinergis_sale_order_client_bloque = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_bloque")
    x_sinergis_sale_order_client_douteux = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_douteux")
    x_sinergis_sale_order_client_suspect = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_suspect")

    x_sinergis_sale_order_objet = fields.Char(string="Objet")
    x_sinergis_sale_order_contact = fields.Many2one("res.partner",string="Contact", required="True")

    fiscal_position_id = fields.Many2one(compute="_compute_fiscal_position_id", readonly=False, domain="[('company_id','=',company_id)]");

    #Empeche l'actualisation automatique de la position fiscale en fonction de la société, nous la recalculons directement en compute en fonction du pays de provenance du client
    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_partner_shipping_id(self):
        SaleOrder._compute_fiscal_position_id(self);
        return {}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.x_sinergis_sale_order_contact = False

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

    @api.depends('fiscal_position_id')
    def _compute_fiscal_position_id (self):
        if self.partner_id :
            if self.state == "draft":
                company_id = self.company_id
                country_id = self.partner_id.country_id.name
                if company_id and country_id :
                    if country_id == "France":
                        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA FRANCE"),('company_id.name', '=', company_id.name)])[0].id
                        self.partner_id.property_account_position_id = self.fiscal_position_id
                    elif country_id == "Guadeloupe" or country_id == "Martinique":
                        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA DOM"),('company_id.name', '=', company_id.name)])[0].id
                        self.partner_id.property_account_position_id = self.fiscal_position_id
                    elif country_id == "Guyane" or country_id == "Guyane française" or country_id=="Saint Barthélémy" or country_id == "Saint-Martin (partie française)" or country_id == "Saint-Martin (partie néerlandaise)":
                        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA EXO"),('company_id.name', '=', company_id.name)])[0].id
                        self.partner_id.property_account_position_id = self.fiscal_position_id
        for order in self:
            order.order_line._compute_tax_id()

    @api.onchange("order_line")
    def on_change_order_line(self):
        for line in self.order_line:
            if line.product_id.name == "CONTRAT D'HEURES PME":
                self.pricelist_id = self.env['product.pricelist'].search([('name','=',"PRIX CONTRAT D'HEURES PME")])
            elif line.product_id.name == "CONTRAT D'HEURES MGE":
                self.pricelist_id = self.env['product.pricelist'].search([('name','=',"PRIX CONTRAT D'HEURES MGE")])

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        SaleOrder._compute_x_sinergis_sale_order_client_bloque(self)
        SaleOrder._compute_x_sinergis_sale_order_client_douteux(self)
        SaleOrder._compute_x_sinergis_sale_order_client_suspect(self)

    #@api.onchange("fiscal_position_id")
    #def on_change_fiscal_position_id(self):
    #    if self.fiscal_position_id:
    #        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',self.fiscal_position_id.name),('company_id.name', '=', self.company_id.name)])[0].id


    #METTRE LES CONDITIONS DE PAIEMENT PAR DEFAUT - OVERRIDE FONCTION DE BASE
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",default=lambda self: self.env['account.payment.term'].search([('name','=',"100% des logiciels et des contrats d'heures et 50% des prestations et formations. Le solde à livraison. à la commande")]))
