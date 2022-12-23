from odoo import models, fields, api
from odoo.exceptions import ValidationError

import math

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_sinergis_sale_order_client_bloque = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_bloque")
    x_sinergis_sale_order_client_douteux = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_douteux")
    x_sinergis_sale_order_client_suspect = fields.Boolean(string="",default=False,compute="_compute_x_sinergis_sale_order_client_suspect")

    x_sinergis_sale_order_objet = fields.Char(string="Objet")
    x_sinergis_sale_order_contact = fields.Many2one("res.partner",string="Contact", required="True")

    fiscal_position_id = fields.Many2one(compute="_compute_fiscal_position_id", readonly=False, domain="[('company_id','=',company_id)]");

    pricelist_id = fields.Many2one(default=lambda self: self.env['product.pricelist'].search([('name','=',"PRIX PUBLIC")]))

    x_sinergis_sale_order_amount_charged = fields.Monetary(string="Montant facturé")
    x_sinergis_sale_order_amount_remaining = fields.Monetary(string="Restant à facturer",compute="_compute_x_sinergis_sale_order_amount_remaining")
    x_sinergis_sale_order_acompte_verse = fields.Boolean(default=0, string="Acompte versé")

    x_sinergis_sale_order_model = fields.Many2one("sale.order",string="Modele de devis")

    x_sinergis_sale_order_product = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('SILAE','SILAE'), ('DIVERS', 'DIVERS')], required=True, string="Produit")

    x_sinergis_sale_order_projects_ended = fields.Boolean(string="Projets terminés", compute="_compute_x_sinergis_sale_order_projects_ended")

    #Empeche l'actualisation automatique de la position fiscale en fonction de la société, nous la recalculons directement en compute en fonction du pays de provenance du client
    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_partner_shipping_id(self):
        SaleOrder._compute_fiscal_position_id(self);
        return {}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.x_sinergis_sale_order_contact = False
        self.partner_invoice_id = self.partner_id
        self.partner_shipping_id = self.partner_id
        if self.partner_id and self.partner_id.company_id:
            self.company_id = self.partner_id.company_id
        else:
            self.company_id = self.env.company.id

    @api.onchange('x_sinergis_sale_order_model')
    def onchange_x_sinergis_sale_order_model(self):
        if self.x_sinergis_sale_order_model:
            #self.env['sale.order.line'].search([('order_id', '=', self.id)]).unlink()
            self.order_line = False
            for line in self.x_sinergis_sale_order_model.order_line:
                data = {
                    'order_id': self.id,
                    'customer_lead': line.customer_lead,
                    'name': line.name,
                    'product_id': line.product_id,
                    'price_unit': line.price_unit,
                    'product_uom_qty': 0
                }
                self.order_line = [(0, 0,data)]


    @api.depends('x_sinergis_sale_order_client_bloque')
    def _compute_x_sinergis_sale_order_client_bloque (self):
        for rec in self:
            if rec.partner_id:
                rec.x_sinergis_sale_order_client_bloque = rec.partner_id.x_sinergis_societe_litige_bloque
            else:
                rec.x_sinergis_sale_order_client_bloque = False

    @api.depends('x_sinergis_sale_order_client_douteux')
    def _compute_x_sinergis_sale_order_client_douteux (self):
        for rec in self:
            if rec.partner_id:
                rec.x_sinergis_sale_order_client_douteux = rec.partner_id.x_sinergis_societe_litige_douteux
            else:
                rec.x_sinergis_sale_order_client_douteux = False

    @api.depends('x_sinergis_sale_order_client_suspect')
    def _compute_x_sinergis_sale_order_client_suspect (self):
        for rec in self:
            if rec.partner_id:
                rec.x_sinergis_sale_order_client_suspect = rec.partner_id.x_sinergis_societe_suspect
            else:
                rec.x_sinergis_sale_order_client_suspect = False

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

    @api.depends('x_sinergis_sale_order_amount_remaining')
    def _compute_x_sinergis_sale_order_amount_remaining (self):
        for rec in self:
            rec.x_sinergis_sale_order_amount_remaining = rec.amount_total - rec.x_sinergis_sale_order_amount_charged


    @api.depends('x_sinergis_sale_order_projects_ended')
    def _compute_x_sinergis_sale_order_projects_ended (self):
        for rec in self:
            project_ids = rec.env['project.project'].search([('sale_order_id', '=', rec.id)])
            projectEnded = True
            if not project_ids:
                projectEnded = False
            for project_id in project_ids:
                if project_id.x_sinergis_project_project_etat_projet != "Projet terminé":
                    projectEnded = False
            rec.x_sinergis_sale_order_projects_ended = projectEnded

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

    @api.onchange("x_sinergis_sale_order_amount_charged")
    def on_change_x_sinergis_sale_order_amount_charged (self):
        self.x_sinergis_sale_order_amount_charged = math.floor(100*self.x_sinergis_sale_order_amount_charged)/100
        if self.x_sinergis_sale_order_amount_charged < 0:
            self.x_sinergis_sale_order_amount_charged = 0
        elif self.x_sinergis_sale_order_amount_charged > self.amount_total:
            self.x_sinergis_sale_order_amount_charged = self.amount_total

    @api.onchange("x_sinergis_sale_order_acompte_verse")
    def on_change_x_sinergis_sale_order_acompte_verse (self):
        project_ids = self.env['project.project'].search([('sale_order_id', '=', self._origin.id)])
        for project_id in project_ids:
            project_id.x_sinergis_project_project_acompte_verse = self.x_sinergis_sale_order_acompte_verse

    #@api.onchange("fiscal_position_id")
    #def on_change_fiscal_position_id(self):
    #    if self.fiscal_position_id:
    #        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',self.fiscal_position_id.name),('company_id.name', '=', self.company_id.name)])[0].id


    #METTRE LES CONDITIONS DE PAIEMENT PAR DEFAUT - OVERRIDE FONCTION DE BASE
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,domain="[ ('company_id', '=', False), ('company_id', '=', company_id)]",default=lambda self: self.env['account.payment.term'].search([('name','ilike',"100% des logiciels")]))

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    purchase_price = fields.Float(
    string='Cost', compute=False,
    digits='Product Price', store=True, readonly=False,
    groups="base.group_user")

#SINERGIS PRODUCTS AND SUB-PRODUCTS
class Products (models.Model):
    _name = "sale.products"
    _description = "Produits"
    name = fields.Char(string="Product Name",required=True)

class SubProducts (models.Model):
    _name = "sale.products.subproducts"
    _description = "Sous-Produits"
    product_id = fields.Many2one("sale.products",string="Produit",required=True)
    name = fields.Char(string="Sub-Product Name",required=True)
