from odoo import models, fields, api

class SinergisAnnualContracts(models.Model):
    _name = "sinergis_x3.annual_contract"
    _description = "Contrats Annuels"

    # Relié via code client X3
    partner_id = fields.Many2one("res.partner",string="Client",required=True)

    # SORDER
    SALFCY = fields.Char(string="Site de vente", required=True) # S1, S2 OU S3
    SOHTYP = fields.Char(string="Type") # REAB OU NEW
    CUSORDREF = fields.Char(string="Type de contrat")
    ORDDAT = fields.Date(string="Date de commande",required=True)

    #SORDERP ET SORDERQ
    TSICOD0 = fields.Char(string="Type d'article")
    TSICOD1 = fields.Char(string="Logiciel")
    TSICOD2 = fields.Char(string="Module")
    TSICOD3 = fields.Char(string="Hébergement")
    TSICOD4 = fields.Char(string="Logiciel")
    ITMDES = fields.Char(string="Désignation")
    X_SERNUM = fields.Char(string="N° de série")
    X_EVO= fields.Char(string="Évolution")
    X_COMEVO = fields.Char(string="Commande évolution")
    X_PERIOD = fields.Char(string="Périodicité")
    X_RENOUVELE = fields.Char(string="Renouvelé")
    STRDAT = fields.Date(string="Début de contrat")
    ENDDAT = fields.Date(string="Fin de contrat")
    QTY = fields.Integer(string="Quantité")
    SAU = fields.Char(string="Unité")
    NETPRI = fields.Float(string="Prix net unitaire")
    PFM = fields.Float(string="Marge unitaire")
    X_RESILIE = fields.Char(string="Résilié")
    X_DATRESIL = fields.Date(string="Date résiliation")
    LASINVNUM = fields.Char(string="No de facture")

    #GACCDUDATE
    AMTLOC = fields.Float(string="Montant échéance")
    PAYLOC = fields.Float(string="Montant payé comptabilisé")
    TMPLOC = fields.Float(string="Montant payé provisoire")

class ResPartner(models.Model):
    _inherit = "res.partner"

    x_sinergis_x3_annual_contract = fields.One2many('sinergis_x3.annual_contract', 'partner_id', string="Contrats annuels X3")
