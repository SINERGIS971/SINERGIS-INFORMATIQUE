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

    #METTRE LES CONDITIONS DE PAIEMENT PAR DEFAUT - OVERRIDE FONCTION DE BASE
    payment_term_id = fields.Many2one(default=lambda self: self.env['account.payment.term'].search([('name','ilike',"100% des logiciels")]))

    #Ancienne version des produits avec anciennes données présentes. À retirer après avoir pleinement adopté le nouveau système.
    x_sinergis_sale_order_product = fields.Selection([('CEGID', 'CEGID'), ('E2TIME', 'E2TIME'), ('MESBANQUES', 'MESBANQUES'), ('OPEN BEE', 'OPEN BEE'), ('QUARKSUP', 'QUARKSUP'), ('SAGE 100', 'SAGE 100'), ('SAGE 1000', 'SAGE 1000'), ('SAP', 'SAP'), ('VIF', 'VIF'), ('X3', 'SAGE X3'), ('XLSOFT', 'XLSOFT'), ('XRT', 'XRT'), ('SILAE','SILAE'), ('DIVERS', 'DIVERS')], required=False, string="Produit")
    #Nouvelle version des produits rattaché au model de produits
    x_sinergis_sale_order_product_new = fields.Many2one("sale.products",string="Produit", required=True)
    x_sinergis_sale_order_product_new_have_subproduct = fields.Boolean(compute="_compute_x_sinergis_sale_order_product_new_have_subproduct") # À actualiser pour pouvoir update la valeur à chaqe chargement de page. Pour le moment, le readonly des subproducts est désactivé

    x_sinergis_sale_order_projects_ended = fields.Boolean(string="Projets terminés", compute="_compute_x_sinergis_sale_order_projects_ended", store=True)

    x_sinergis_sale_res_users_job = fields.Selection(related="user_id.x_sinergis_res_users_job", store="True") #Type du vendeur : Consultant ou commercial

    # 3 Janvier 2023 : Pouvoir modifier la date de commande
    date_order = fields.Datetime(readonly=False)

    # 26 Janvier 2023 : Ajout du nombre de jours prévus / réalisés / restants / (planifiés) dans la vue liste
    #Nous prenons en compte qu'une journée dure 8h
    x_sinergis_sale_order_scheduled_days = fields.Float(string="Jours prévus", compute="_compute_x_sinergis_sale_order_scheduled_days")
    x_sinergis_sale_order_completed_days = fields.Float(string="Jours réalisés", compute="_compute_x_sinergis_sale_order_completed_days")
    x_sinergis_sale_order_remaining_days = fields.Float(string="Jours restants", compute="_compute_x_sinergis_sale_order_remaining_days")
    x_sinergis_sale_order_planned_days = fields.Float(string="Jours planifiés", compute="_compute_x_sinergis_sale_order_planned_days")

    # 27 Janvier 2023 : Ajout d'une case 'Commande fournisseur' qui permet de savoir si les licences sont déjà commandées.

    x_sinergis_sale_order_supplier_order = fields.Boolean(string="Commande fournisseur", default=False)



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

    @api.onchange('x_sinergis_sale_order_product_new')
    def onchange_x_sinergis_sale_order_product_new(self):
        for line in self.order_line :
            line.x_sinergis_sale_order_line_subproduct_id = False


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

    @api.depends('x_sinergis_sale_order_product_new_have_subproduct')
    def _compute_x_sinergis_sale_order_product_new_have_subproduct (self):
        for rec in self:
            state = False
            if rec.x_sinergis_sale_order_product_new:
                if self.env['sale.products.subproducts'].search([('product_id','=',rec.x_sinergis_sale_order_product_new.id)]):
                    state = True
            rec.x_sinergis_sale_order_product_new_have_subproduct = state

    @api.depends("x_sinergis_sale_order_scheduled_days")
    def _compute_x_sinergis_sale_order_scheduled_days (self):
        for rec in self:
            scheduled_days = 0
            tasks = self.env['project.task'].search([('sale_order_id','=',rec.id)])
            for task in tasks:
                # Une journée correspond à 8 heures
                scheduled_days += task.planned_hours / 8
            scheduled_days = round(scheduled_days,2)
            rec.x_sinergis_sale_order_scheduled_days = scheduled_days

    @api.depends("x_sinergis_sale_order_completed_days")
    def _compute_x_sinergis_sale_order_completed_days (self):
        for rec in self:
            completed_days = 0
            tasks = self.env['project.task'].search([('sale_order_id','=',rec.id)])
            for task in tasks:
                # Une journée correspond à 8 heures
                completed_days += task.effective_hours / 8
            completed_days = round(completed_days,2)
            rec.x_sinergis_sale_order_completed_days = completed_days

    @api.depends("x_sinergis_sale_order_remaining_days")
    def _compute_x_sinergis_sale_order_remaining_days (self):
        for rec in self:
            remaining_days = 0
            tasks = self.env['project.task'].search([('sale_order_id','=',rec.id)])
            for task in tasks:
                # Une journée correspond à 8 heures
                remaining_days += task.remaining_hours / 8
            completed_days = round(remaining_days,2)
            rec.x_sinergis_sale_order_remaining_days = remaining_days

    @api.depends("x_sinergis_sale_order_planned_days")
    def _compute_x_sinergis_sale_order_planned_days (self):
        for rec in self:
            planned_days = 0
            tasks = self.env['project.task'].search([('sale_order_id','=',rec.id)])
            for task in tasks:
                # Une journée correspond à 8 heures
                planned_days += task.x_sinergis_project_task_planned_hours / 8
            planned_days = round(planned_days,2)
            rec.x_sinergis_sale_order_planned_days = planned_days

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

    # Code de l'ancien système d'acompte versé avec les projets
    #@api.onchange("x_sinergis_sale_order_acompte_verse")
    #def on_change_x_sinergis_sale_order_acompte_verse (self):
    #    project_ids = self.env['project.project'].search([('sale_order_id', '=', self._origin.id)])
    #    for project_id in project_ids:
    #        project_id.x_sinergis_project_project_acompte_verse = self.x_sinergis_sale_order_acompte_verse

    #@api.onchange("fiscal_position_id")
    #def on_change_fiscal_position_id(self):
    #    if self.fiscal_position_id:
    #        self.fiscal_position_id = self.env['account.fiscal.position'].search([('name','=',self.fiscal_position_id.name),('company_id.name', '=', self.company_id.name)])[0].id

    # 26 Février 2023 - Lors de la suppression d'un devis / bon de commande, supprimer aussi les tâches et projets associés
    def unlink(self):
        for rec in self:
            self.env['project.task'].sudo().search(['|', ('sale_line_id', 'in', rec.order_line.ids),('sale_order_id', '=', rec.id)]).unlink()
            self.env['project.project'].sudo().search([('sale_order_id', '=', rec.id)]).unlink()
        return super(SaleOrder, self).unlink()



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    purchase_price = fields.Float(
    string='Cost', compute=False,
    digits='Product Price', store=True, readonly=False,
    groups="base.group_user")
    x_sinergis_sale_order_line_subproduct_id = fields.Many2one("sale.products.subproducts",string="Sous-Produit")

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
