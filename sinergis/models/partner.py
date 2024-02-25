# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

from datetime import datetime


class ResPartner(models.Model):

    _inherit = "res.partner"

    # --KANBAN--

    #Fonction pour changer la couleur en fonction du statut (bloqué/douteux)
    def change_colore_on_kanban(self):
        for record in self:
            if record.x_sinergis_societe_litige_bloque :
                color = 1
            elif record.x_sinergis_societe_litige_douteux:
                color = 2
            else :
                color = 0
            record.color = color
    color = fields.Integer('Color Index', compute="change_colore_on_kanban") #Variable qui stockera la couleur de la bande gauche de la socété dans le kanban

    # --FORM--

    company_id = fields.Many2one(default=lambda self: self.env.company)

    x_sinergis_societe_mere = fields.Many2one('res.partner', string="Société mère", index=True)

    x_sinergis_societe_suspect = fields.Boolean(string="Suspect")
    x_sinergis_societe_suspect_text = fields.Char(string="", default="Suspect")
    x_sinergis_societe_type = fields.Char(string="Statut", readonly=True)
    x_sinergis_societe_en_cours_immatriculation = fields.Boolean(string="En cours d'immatriculation")
    x_sinergis_societe_nom_juridique = fields.Char(string="Nom juridique")
    x_sinergis_societe_autre_nom = fields.Char(string="Autre nom")
    x_sinergis_societe_secteurs = fields.Many2many('x_sinergis_secteur_s',string='Secteurs')

    x_sinergis_societe_activite = fields.Char(string='Activité')
    x_sinergis_societe_effectif = fields.Char(string='Effectif')
    x_sinergis_societe_ancien_code_sap = fields.Char(string='Ancien code SAP')
    x_sinergis_societe_ancien_code_x3 = fields.Char(string='Ancien code X3')
    x_sinergis_societe_code_client_sage = fields.Char(string='Code client SAGE')
    x_sinergis_societe_compte_tiers = fields.Char(string='Compte Tiers')

    write_date = fields.Datetime(string='Dernière mise à jour le :')

    x_sinergis_societe_litige_douteux = fields.Boolean(string="Douteux")
    x_sinergis_societe_litige_douteux_remarques = fields.Text(string="Remarques")
    x_sinergis_societe_litige_bloque = fields.Boolean(string="Bloqué")
    x_sinergis_societe_litige_bloque_remarques = fields.Text(string="Remarques")

    x_sinergis_societe_notes_techniques = fields.Text(string="Notes techniques")
    x_sinergis_societe_fichier_notes_techniques = fields.One2many('sinergis.technical_note_files', 'partner_id', string="Fichiers notes techniques")

    x_sinergis_societe_societe_fille = fields.One2many('res.partner', 'x_sinergis_societe_mere', string='Contact', domain=[('active', '=', True)]) #EN TEST

    x_sinergis_societe_suivi_activite = fields.One2many('project.task', 'commercial_partner_id',related="commercial_partner_id.task_ids",readonly=True)

    x_sinergis_societe_annual_contracts = fields.One2many('sinergis.annual_contracts', 'partner_id', string="Contrats annuels")

    # 8/03/2023 : Ajout du statut "étranger" pour avoir libre choix de la TVA lors de la facturation

    x_sinergis_societe_etranger = fields.Boolean(string="Étranger", default=False)

    # 29/08/2023 : Ajout d'un champ afin de savoir si la société possère un payeur
    x_sinergis_societe_has_payer = fields.Boolean(string="Possède un payeur", compute="_compute_x_sinergis_societe_has_payer")

    # 19/01/2024 : Permet de voir si le client est un client burst ou non.
    x_sinergis_societe_is_burst = fields.Boolean(string="Client BURST")

    # 24/01/2024 : Champs permettant la sécurisation des données techniques du client
    x_sinergis_societe_technical_notes_allowed = fields.Boolean(compute="_compute_x_sinergis_societe_technical_notes_allowed")

    #Gestion des contraintes supplémentaires

    @api.constrains("child_ids")
    def constraint_x_sinergis_child_ids(self):
        isEmpty = 1
        for rec in self.child_ids:
            isEmpty = 0
        if isEmpty == 1 :
            raise ValidationError("Il vous faut au moins un contact associé à la société.")


    #Gestion des changements de champs

    @api.onchange("x_sinergis_societe_suspect")
    def on_change_x_sinergis_societe_suspect(self):
        if self.x_sinergis_societe_suspect:
            self.x_sinergis_societe_litige_douteux = 0
            self.x_sinergis_societe_litige_douteux_remarques = ""
            self.x_sinergis_societe_litige_bloque = 0
            self.x_sinergis_societe_litige_bloque_remarques = ""

    @api.onchange("x_sinergis_societe_en_cours_immatriculation")
    def on_change_x_sinergis_societe_en_cours_immatriculation(self):
        res = {}
        if self.x_sinergis_societe_en_cours_immatriculation:
            self.siret = ""

    @api.onchange("zip")
    def on_change_zip(self):
        zip = self.zip
        if type(zip).__name__ == "str":
            zipList = list(zip)
            if len(zip) == 5:
                zip = ''.join(zipList[:3])
                if zip == "971":
                    self.company_id = 1
                elif zip == "972":
                    self.company_id = 2
                elif zip == "973":
                    self.company_id = 3


    # TO DO: Voir si on peut sélécitonner la position fiscale différament qu'avec l'ID
    @api.onchange("country_id")
    def on_change_country_id(self):
        if self.is_company == True :
            company_id = self.company_id
            country_id = self.country_id.name
            if company_id and country_id :
                if country_id == "France":
                    self.property_account_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA FRANCE"),('company_id.name', '=', company_id.name)])[0].id
                elif country_id == "Guadeloupe" or country_id == "Martinique":
                    self.property_account_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA DOM"),('company_id.name', '=', company_id.name)])[0].id
                elif country_id == "Guyane" or country_id == "Guyane française" or country_id=="Saint Barthélémy" or country_id == "Saint-Martin (partie française)" or country_id == "Saint-Martin (partie néerlandaise)":
                    self.property_account_position_id = self.env['account.fiscal.position'].search([('name','=',"TVA EXO"),('company_id.name', '=', company_id.name)])[0].id


    @api.onchange("x_sinergis_societe_litige_douteux")
    def on_change_x_sinergis_societe_litige_douteux(self):
        self.x_sinergis_societe_litige_douteux_remarques = ""
        ResPartner.sinergisLitige(self)

    @api.onchange("x_sinergis_societe_litige_bloque")
    def on_change_x_sinergis_societe_litige_bloque(self):
        self.x_sinergis_societe_litige_bloque_remarques = ""
        ResPartner.sinergisLitige(self)
        #if self.x_sinergis_societe_litige_bloque: #SEND MAIL
        #    self.env.ref('sinergis.sinergis_mail_societe_bloque').with_context().send_mail(self.id,force_send=True)
        #    template.send_mail(self.id, force_send=True)

    @api.depends("x_sinergis_societe_has_payer")
    def _compute_x_sinergis_societe_has_payer(self):
        for rec in self:
            payer_ids = self.env['res.partner'].search([('parent_id','=',rec.id),('x_sinergis_societe_contact_payer','=',True)])
            rec.x_sinergis_societe_has_payer = len(payer_ids) > 0

    @api.depends("x_sinergis_societe_technical_notes_allowed")
    def _compute_x_sinergis_societe_technical_notes_allowed (self):
        for rec in self:
            if self.env.user.x_sinergis_res_users_partner_technical_notes_limit < datetime.now():
                rec.x_sinergis_societe_technical_notes_allowed = False
            else :
                rec.x_sinergis_societe_technical_notes_allowed = True


    def sinergisLitige(self):
        douteux = self.x_sinergis_societe_litige_douteux
        bloque = self.x_sinergis_societe_litige_bloque
        if (douteux and bloque):
            self.x_sinergis_societe_type = "Client douteux et bloqué !"
        elif (douteux):
            self.x_sinergis_societe_type = "Client douteux !"
        elif (bloque):
            self.x_sinergis_societe_type = "Client bloqué !"
        else:
            self.x_sinergis_societe_type = ""

            # -- CREATION DE CONTACT --

    x_sinergis_societe_contact_firstname = fields.Char(string='Prenom')
    x_sinergis_societe_contact_lastname = fields.Char(string='Nom')

    x_sinergis_societe_contact_metier = fields.Many2many('x_metier',string='Metier')

    x_sinergis_societe_contact_facturation_street = fields.Char(string='Rue')
    x_sinergis_societe_contact_facturation_street2 = fields.Char(string='Rue 2')
    x_sinergis_societe_contact_facturation_city = fields.Char(string='Ville')
    x_sinergis_societe_contact_facturation_zip = fields.Char(string='Code postal')
    x_sinergis_societe_contact_facturation_country_id = fields.Many2one('res.country',string='Pays')

    x_sinergis_societe_contact_inactive = fields.Boolean(string="Contact inactif")
    x_sinergis_societe_contact_inactive_reason = fields.Html(string="Raison de l'inactivité")

    x_sinergis_societe_contact_payer = fields.Boolean(string="Payeur")


    @api.onchange("x_sinergis_societe_contact_firstname")
    def on_change_x_sinergis_societe_contact_firstname(self):
        firstname = self.x_sinergis_societe_contact_firstname
        if type(firstname).__name__ == "str":
            if len(firstname) > 0:
                firstname = firstname.lower()
                firstnameList = list(firstname)
                firstnameList[0] = firstname[0].upper()
                self.x_sinergis_societe_contact_firstname = "".join(firstnameList)
            ResPartner.update_name(self)


    @api.onchange("x_sinergis_societe_contact_lastname")
    def on_change_x_sinergis_societe_contact_lastname(self):
        lastname = self.x_sinergis_societe_contact_lastname
        if type(lastname).__name__ == "str":
            if len(lastname) > 0:
                self.x_sinergis_societe_contact_lastname = lastname.upper()
                ResPartner.update_name(self)

    #@api.onchange("x_sinergis_societe_contact_payer")
    #def on_change_x_sinergis_societe_contact_payer(self):
    #    if self._origin.parent_id and self.x_sinergis_societe_contact_payer:
    #        contact_ids = self.env['res.partner'].search([('parent_id','=',self._origin.parent_id.id),('x_sinergis_societe_contact_payer','=',True)])
    #        if len(contact_ids) > 0:
    #            self.x_sinergis_societe_contact_payer = False
    #            raise ValidationError("Un payeur existe déjà pour ce client. Vous ne pouvez spécifier qu'un seul payeur par client")


    def update_name(self):
        firstname = self.x_sinergis_societe_contact_firstname
        lastname = self.x_sinergis_societe_contact_lastname
        if type(lastname).__name__ != "str":
            lastname = ""
        if type(firstname).__name__ != "str":
            firstname = ""

        if firstname != False and firstname != "":
            self.name = lastname + " " + firstname
        else :
            self.name = lastname

    #Bouton "Rendez-vous" lié au calendrier: Remplacement de la fonction pour faire passer la société dans les valeurs transférées
    def sinergis_schedule_meeting(self):
        self.ensure_one()
        partner_ids = self.ids
        partner_ids.append(self.env.user.partner_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_partner_ids': partner_ids,
            'default_x_sinergis_calendar_event_client': self.id,
        }
        action['domain'] = ['|', ('id', 'in', self._compute_meeting()[self.id]), ('partner_ids', 'in', self.ids)]
        return action
    
    #Bouton permettant de débloquer les notes techniques :
    def x_sinergis_societe_unlock_technical_notes_button(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'sinergis_unlock_technical_notes',
            'target': 'new',
        }

    #Supprimer les contacts de la société
    def unlink (self):
        for societe in self:
            societe.search([('parent_id', '=', societe.id)]).unlink()
        return super(ResPartner,self).unlink()


    def write(self, values):
        # Si modification du code client X3
        if "sinergis_x3_code" in values:
            # Suppression des contrats annuels du client
            self.env["sinergis_x3.annual_contract"].sudo().search([('partner_id','=',self.id)]).unlink()
        #Envoyer un mail si la société est bloquée ou débloquée
        if "x_sinergis_societe_litige_bloque" in values:
            if self.x_sinergis_societe_litige_bloque == False and values["x_sinergis_societe_litige_bloque"] == True:
                template_id = self.env.ref('sinergis.sinergis_mail_res_partner_litige_bloque').id
                self.env["mail.template"].browse(template_id).with_context(reason=values["x_sinergis_societe_litige_bloque_remarques"]).send_mail(self.id, force_send=True)
            elif self.x_sinergis_societe_litige_bloque == True and values["x_sinergis_societe_litige_bloque"] == False:
                template_id = self.env.ref('sinergis.sinergis_mail_res_partner_litige_debloque').id
                self.env["mail.template"].browse(template_id).send_mail(self.id, force_send=True)
        return super(ResPartner, self).write(values)

# A SUPPRIMER
class SinergisAnnualContracts(models.Model):
    _name = "sinergis.annual_contracts"
    _description = "Contrats Annuels"

    # Relié via code client X3
    partner_id = fields.Many2one("res.partner",string="Client",required=True)

class SinergisTechnicalNoteFiles(models.Model):
    _name = "sinergis.technical_note_files"
    _description = "Fichiers Note Technique"

    partner_id = fields.Many2one("res.partner",string="Client",required=True)

    name = fields.Char(string="Nom",required=True)
    file = fields.Binary(string="File", required=True)
