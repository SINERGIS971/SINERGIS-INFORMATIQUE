from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from datetime import date
from datetime import datetime
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
import secrets


#Pour le téléchargement de tous les documents
import os, shutil


class Training(models.Model):
    _name = "training"
    _inherit = ["mail.thread"]
    _description = "Formations"

    active = fields.Boolean(string='Active', default=True)

    sale_id = fields.Many2one("sale.order", string="Devis")
    sale_order_line_id = fields.Many2one("sale.order.line")

    # Heures réalisées, prévues, restantes, planifiées
    scheduled_hours = fields.Float(string="Heures planifiées", compute="_compute_task_hours")
    planned_hours = fields.Float(string="Heures prévues", compute="_compute_task_hours")
    effective_hours = fields.Float(string="Heures effectuées", compute="_compute_task_hours")
    remaining_hours = fields.Float(string="Heures restantes", compute="_compute_task_hours")

    #Quiz tokens
    token_delayed_assessment = fields.Char(default="")
    token_opco_quiz = fields.Char(default="")

    state = fields.Selection([('unassigned', 'Non assigné'),('commercial_part','Partie commerciale'),('consultant_part','Partie consultant'),('training_in_progress','Formation en cours'),('training_ended','Formation terminée'),('training_closed','Formation cloturée')], string="État",default="unassigned")
    name = fields.Char(string="Nom")
    #Unassigned part
    sales_manager = fields.Many2one("res.users",string='Responsable commercial')
    signed_quote = fields.Binary(string='Devis signé', related='sale_id.x_sinergis_sale_order_signed_quote', readonly=True)
    #Commercial part
    partner_id = fields.Many2one("res.partner", related='sale_order_line_id.training_partner_id', string="Client", readonly=True, store=True)
    partner_manager_id = fields.Many2one("res.partner", string="Référent client")
    company_id = fields.Many2one("res.company", string="Société Sinergis")
    type_id = fields.Many2one("training.type", string="Type de formation")
    type_product_id = fields.Many2one("training.type.product", string="Produit")
    type_product_plan_id = fields.Many2one("training.type.product.plan",string="Plan de formation")
    diagnosis_file = fields.Binary(string="Diagnostic initial")
    opco_id = fields.Many2one("training.opco", string="OPCO")
    opco_file = fields.Binary(string="Document OPCO")
    training_participants = fields.One2many("training.participants","training_id",string="Participants à la formation")
    #Commercial part - Drafting of the agreement
    course_title = fields.Text(string="Intitulé du stage")
    location = fields.Many2one("training.location", string="Localisation de la formation (département)")
    start = fields.Date(string="Début de la formation")
    end = fields.Date(string="Fin de la formation")
    duration = fields.Float(string="Durée (jours)",compute="_compute_duration")
    duration_hours = fields.Float(string="Durée (heures)",compute="_compute_duration_hours")
    #agreement_internal_signer = fields.Char(string="Signataire interne de la convention",default="Alain CASIMIRO, Directeur")
    agreement_internal_signer = fields.Many2one("training.agreement_internal_signer",string='Signataire interne de la convention', default=lambda self: self.env['training.agreement_internal_signer'].search([('user_id.name','=','CASIMIRO Alain')]))

    signed_agreement = fields.Binary(string='Convention de formation signée')

    #Consultant part

    consultant_id = fields.Many2one("res.users",string='Consultant')
    location_selection = fields.Selection([('company', 'Agence SINERGIS'),('client','Chez le client'),('other','Autre')], string="Localisation")
    location_street = fields.Char(string='Rue')
    location_street2 = fields.Char(string='Rue 2')
    location_city = fields.Char(string='Ville')
    location_zip = fields.Char(string='Code postal')
    location_country_id = fields.Many2one('res.country',string='Pays')
    remote_learning = fields.Boolean(string='Formation à distance ?', default=False)
    remote_learning_link = fields.Char(string="Lien de la formation")
    planned_hours_ids = fields.One2many("calendar.event","training_id",string="Heures de formation planifiées",readonly=True)
    planned_hours_alert = fields.Html(string="", compute="_compute_planned_hours_alert") # Message d'alerte si les conditions sur les heures de formations ne sont pas respectées

    #Training ended part

    evaluating_training_course = fields.Selection([('very_satisfaying', 'Très satisfaisant'),('satisfaying','Satisfaisant'),('perfectible','Perfectible'),('insufficient','Insuffisant')], string="Evaluation du déroulement")
    difficulties_training_course = fields.Text(string="Précisez si difficultés rencontrées :")
    # Ancien système < 17/02/2023
    # signed_attendance_sheet = fields.Binary(string="Feuille d'émargement remplie")
    # Nouveau système > 17/02/2023
    signed_attendance_sheets = fields.One2many('training.attendance_sheet', 'training_id', string="Feuilles d'émargement remplies")

    #Training closed part
    training_closed_date = fields.Date(string="Date de cloture de la formation", default=False,readonly=True)

    delayed_assessment_sent = fields.Boolean(string="Évaluation à froid envoyée",default=False,readonly=True)
    answer_delayed_assessment = fields.Html(default="",readonly=True, string="Réponses de l'évaluation à froid")
    mark_delayed_assessment = fields.Float(string="Note de l'évaluation à froid")
    delayed_assessment_received = fields.Boolean(string="Évaluation à froid reçue",default=False,compute="_compute_delayed_assessment_received")

    opco_quiz_sent = fields.Boolean(string="Quiz OPCO envoyé",default=False,readonly=True)
    mark_opco_quiz = fields.Float(string="Note du quiz OPCO")
    answer_opco_quiz = fields.Html(default="",readonly=True, string="Réponses du quiz OPCO")
    opco_quiz_received = fields.Boolean(string="Quiz OPCO reçu",default=False,compute="_compute_opco_quiz_received")

    #Stats part

    sale_price_total = fields.Float(string="Prix de la formation",compute="_compute_sale_price_total",store=True)
    participants_count = fields.Integer(string="Nombre de participants",store=True,compute="_compute_participants_count")



    @api.onchange("type_id")
    def on_change_type_id(self):
        self.type_product_id = False
        self.type_product_plan_id = False

    @api.onchange("type_product_id")
    def on_change_type_product_id(self):
        self.type_product_plan_id = False

    @api.onchange("location_selection")
    def on_change_location_selection(self):
        if self.location_selection == "company":
            self.location_street = self.company_id.street
            self.location_street2 = self.company_id.street2
            self.location_city = self.company_id.city
            self.location_zip = self.company_id.zip
            self.location_country_id = self.company_id.country_id
        elif self.location_selection == "client":
            self.location_street = self.partner_id.street
            self.location_street2 = self.partner_id.street2
            self.location_city = self.partner_id.city
            self.location_zip = self.partner_id.zip
            self.location_country_id = self.partner_id.country_id
        elif self.location_selection == "other":
            self.location_street = False
            self.location_street2 = False
            self.location_city = False
            self.location_zip = False
            self.location_country_id = False

    @api.onchange("company_id")
    def on_change_company_id (self):
        # Signataire interne lié à la société Sinergis.
        self.agreement_internal_signer = False

    # Ne pas autoriser de mettre une date de début ou fin dans le mauvais sens
    @api.onchange("start")
    def on_change_start(self):
        if self.end and self.start:
            if self.end < self.start:
                raise ValidationError("Attention ! La date de début est supérieure à la date de fin.")
            
    @api.onchange("end")
    def on_change_end(self):
        if self.end and self.start:
            if self.end < self.start:
                raise ValidationError("Attention ! La date de fin est inférieure à la date de début.")

    @api.depends('planned_hours','effective_hours','remaining_hours',"scheduled_hours")
    def _compute_task_hours(self):
        for rec in self:
            task = self.env["project.task"].search([("sale_line_id", "=", rec.sale_order_line_id.id)], limit=1)
            rec.planned_hours = task.planned_hours
            rec.effective_hours = task.effective_hours
            rec.remaining_hours = task.remaining_hours
            scheduled_hours = 0
            for planned_hour in rec.planned_hours_ids:
                scheduled_hours += planned_hour.duration
            rec.scheduled_hours = scheduled_hours


    # Détecte une erreur dans l'enregistrement des heures de formation
    # - Si les heures planifiées dépassent celles du bon de commande
    # - Si les heures planifiées sont insuffisantes par rapport à celles du bon de commande
    # - Si une des dates de formation est en dehors du début/fin des dates de la formation
    @api.depends('planned_hours_alert')
    def _compute_planned_hours_alert (self):
        for rec in self:
            total_hours = 0
            too_early = False
            too_late = False
            for event in rec.planned_hours_ids:
                total_hours += event.duration
                if event.start.date() < rec.start or event.stop.date() < rec.start :
                    too_early = True
                if event.start.date() > rec.end or event.stop.date() > rec.end  :
                    too_late = True
            messages = []
            if total_hours > rec.duration_hours and total_hours > 0 :
                messages.append(f"- Vous avez planifié plus d'heures que prévues. La convention de formation indique un total de {rec.duration_hours} heures alors que vous avez placé {total_hours} heures.")
            elif total_hours < rec.duration_hours and total_hours > 0 :
                messages.append(f"- Vous avez planifié moins d'heures que prévues. La convention de formation indique un total de {rec.duration_hours} heures alors que vous avez placé {total_hours} heures.")
            if too_early :
                messages.append(f"- Au moins un évènement Formation a été placé trop tôt. La convention de formation de formation indique un début le : {rec.start.strftime('%d/%m/%Y')}")
            if too_late :
                messages.append(f"- Au moins un évènement Formation a été placé trop tard. La convention de formation de formation indique une fin le : {rec.end.strftime('%d/%m/%Y')}")
            message = '<br/>'.join(messages)
            rec.planned_hours_alert = message


    @api.depends('delayed_assessment_received')
    def _compute_delayed_assessment_received (self):
        for rec in self:
            if rec.answer_delayed_assessment:
                rec.delayed_assessment_received = True
            else:
                rec.delayed_assessment_received = False

    @api.depends('opco_quiz_received')
    def _compute_opco_quiz_received (self):
        for rec in self:
            if rec.answer_opco_quiz:
                rec.opco_quiz_received = True
            else:
                rec.opco_quiz_received = False

    @api.depends('sale_price_total')
    def _compute_sale_price_total (self):
        for rec in self:
            if rec.sale_order_line_id:
                rec.sale_price_total = rec.sale_order_line_id.price_total
            else:
                rec.sale_price_total = 0

    @api.depends("participants_count")
    def _compute_participants_count (self):
        for rec in self:
            rec.participants_count = len(rec.training_participants)

    @api.depends("duration", "partner_manager_id")
    def _compute_duration (self):
        for rec in self:
            if rec.sale_order_line_id.product_uom.name == "Heures":
                rec.duration = round(rec.sale_order_line_id.product_uom_qty/7, 2)
            else:
                rec.duration = rec.sale_order_line_id.product_uom_qty

    @api.depends("duration_hours")
    def _compute_duration_hours (self):
        for rec in self:
            #Une journée de formation correspond à 7 heures
            if rec.sale_order_line_id.product_uom.name == "Heures":
                rec.duration = rec.sale_order_line_id.product_uom_qty
            else:
                rec.duration_hours = 7.0 * rec.duration

    #Header buttons

    def verifiation_fields(self):
        missing_elements = []
        if self.state == "unassigned":
            if not self.sales_manager :
                missing_elements.append("Responsable commercial")
            if not self.signed_quote :
                missing_elements.append("Devis signé")

        if self.state == "commercial_part":
            if not self.partner_id :
                missing_elements.append("Client")
            if not self.partner_manager_id :
                missing_elements.append("Référent client")
            if not self.company_id :
                missing_elements.append("Société Sinergis")
            if not self.type_id :
                missing_elements.append("Type de formation")
            if not self.type_product_id :
                missing_elements.append("Produit")
            if not self.type_product_plan_id :
                missing_elements.append("Plan de formation")
            if not self.diagnosis_file :
                missing_elements.append("Diagnostic initial")
            if not self.course_title :
                missing_elements.append("Intitulé du stage")
            if not self.location :
                missing_elements.append("Localisation de la formation")
            if not self.start :
                missing_elements.append("Début de la formation")
            if not self.end :
                missing_elements.append("Fin de la formation")
            if not self.agreement_internal_signer:
                missing_elements.append("Signataire interne de la convention")
            if not self.signed_agreement :
                missing_elements.append("Convention de formation signée")

        if self.state == "consultant_part":
            if not self.consultant_id :
                missing_elements.append("Consultant")
            if not self.remote_learning_link and self.remote_learning == True :
                missing_elements.append("Lien de la formation")
            if self.remote_learning == False:
                if not self.location_selection :
                    missing_elements.append("Localisation")
                if not self.remote_learning:
                    if self.location_selection == "other":
                        if not self.location_street :
                            missing_elements.append("Adresse de localisation (Rue)")
                        if not self.location_city :
                            missing_elements.append("Adresse de localisation (Ville)")
                        if not self.location_zip :
                            missing_elements.append("Adresse de localisation (Code Postal)")
                        if not self.location_country_id :
                            missing_elements.append("Adresse de localisation (Pays)")
            if not self.planned_hours_ids :
                missing_elements.append("Heures de formation planifiées")

        if self.state == "training_ended":
            if len(self.signed_attendance_sheets) == 0 :
                missing_elements.append("Feuille(s) d'émargement remplie(s)")
            if not self.evaluating_training_course :
                missing_elements.append("Evaluation du déroulement")


        if len(missing_elements) != 0 :
            raise ValidationError("Il vous manque les éléments suivants : "+', '.join(missing_elements)+" pour passer à la partie suivante.")
        else :
            return True


    def button_switch_commercial_part(self):
        if Training.verifiation_fields(self):
            self.state = "commercial_part"

    def button_return_unassigned(self):
        self.state = "unassigned"

    def button_switch_consultant_part(self):
        if Training.verifiation_fields(self):
            self.state = "consultant_part"

    def button_return_commercial_part (self):
        self.state = "commercial_part"

    def button_switch_training_in_progress_part (self):
        if Training.verifiation_fields(self):
            self.state = "training_in_progress"

    def button_return_consultant_part (self):
        self.state = "consultant_part"

    def button_switch_training_ended_part (self):
        if Training.verifiation_fields(self):
            self.state = "training_ended"

    def button_return_training_in_progress_part (self):
        self.state = "training_in_progress"

    def button_switch_training_closed_part (self):
        if Training.verifiation_fields(self):
            if not self.training_closed_date:
                self.training_closed_date = today = date.today()
            self.state = "training_closed"

    def button_return_training_ended_part (self):
        self.state = "training_ended"

    def button_download_attendance_sheet (self):
        if Training.verification_training_attendance_sheet(self):
            return self.env.ref('training.training_attendance_sheet_report').report_action(self)
    def button_download_certificate_of_attendance (self):
        if Training.verification_training_attendance_sheet(self):
            return self.env.ref('training.training_certificate_of_attendance').report_action(self)

    def verification_training_attendance_sheet(self):
        missing_elements = []
        if not self.company_id :
            missing_elements.append("Société SINERGIS")
        if not self.start :
            missing_elements.append("Début de la formation")
        if not self.end :
            missing_elements.append("Fin de la formation")
        if not self.consultant_id :
            missing_elements.append("Consultant")
        if len(missing_elements) != 0 :
            raise ValidationError("Il vous manque les éléments suivants : "+', '.join(missing_elements)+" pour générer la feuille d'émargement")
        else :
            return True

    #Button box

    def action_open_sale_id (self):
        return {
            'name': 'Devis',
            'type': 'ir.actions.act_window',
            "views": [[False, "form"]],
            'res_model': 'sale.order',
            'res_id': self.sale_id.id,
        }
    
    def action_open_sended_mail(self):
        participants_ids = self.env['training.participants'].search([('training_id','=', self.id)])
        mails = self.env["mail.mail"].search(['|','&',("res_id","in",participants_ids.ids),('model','=','training.participants'),'&',("res_id","=",self.id),('model','=','training')]) 
        #tree_view_id = self.env.ref('sinergis.sinergis_email_sent_tree').id
        return {
            'name': 'Emails envoyés concernant la formation',
            'type': 'ir.actions.act_window',
            "views": [[False, "tree"],[False, "form"]],
            'res_model': 'mail.mail',
            'domain': f"[('id','in',{mails.ids})]",
        }

    #Other buttons

    def verification_training_agreement(self):
        missing_elements = []
        if not self.sales_manager :
            missing_elements.append("Responsable commercial")
        if not self.partner_id :
            missing_elements.append("Client")
        if not self.partner_manager_id :
            missing_elements.append("Référent client")
        if not self.company_id :
            missing_elements.append("Société SINERGIS")
        if not self.type_id :
            missing_elements.append("Type de formation")
        if not self.type_product_id :
            missing_elements.append("Produit")
        if not self.type_product_plan_id :
            missing_elements.append("Plan de formation")
        if not self.training_participants :
            missing_elements.append("Participants à la formation")
        if not self.course_title :
            missing_elements.append("Intitulé du stage")
        if not self.location :
            missing_elements.append("Localisation de la formation")
        if not self.start :
            missing_elements.append("Début de la formation")
        if not self.end :
            missing_elements.append("Fin de la formation")
        if not self.agreement_internal_signer:
            missing_elements.append("Signataire interne de la convention")

        if len(missing_elements) != 0 :
            raise ValidationError("Il vous manque les éléments suivants : "+', '.join(missing_elements)+" pour passer à la partie suivante.")
        else :
            return True

    def download_training_agreement(self):
        if Training.verification_training_agreement(self):
            return self.env.ref('training.training_agreement_report').report_action(self)
        
    def download_training_quiz_answers(self):
        return self.env.ref('training.training_quiz_report').report_action(self)
    
    def download_all_documents(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": f"{str(base_url)}/training/download_all?training_id={str(self.id)}",
            "target": "new",
        }


    def send_training_agreement(self):
        if Training.verification_training_agreement(self):
            self.ensure_one()
            #ir_model_data = self.env['ir.model.data']
            temp_id = self.env.ref('training.training_agreement_name')
            attach_obj = self.env['ir.attachment']

            attachment_ids = []
            #Training plan (PDF)
            if self.type_product_plan_id:
                if self.type_product_plan_id.training_plan_file:
                    result_training_plan = self.type_product_plan_id.training_plan_file
                    attach_data = {
                        'name': self.type_product_plan_id.name+'.pdf',
                        'datas': result_training_plan,
                        'res_model': 'ir.ui.view',
                    }
                    attach_id = attach_obj.create(attach_data)
                    attachment_ids.append(attach_id.id)
            temp_id.write({'attachment_ids': [(6, 0, attachment_ids)]})
            ctx = dict(self.env.context or {})
            ctx.update({
                'default_model': 'training',
                'default_res_id': self.ids[0],
                'default_use_template': bool(temp_id.id),
                'default_template_id': temp_id.id,
                'default_composition_mode': 'comment',
            })
            return {
                'name': 'Compose Email',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    def button_plan_training_slot(self):
        if self.partner_id:
            self.ensure_one()
            action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
            action['context'] = {
                'default_res_id': self.id,
                'default_res_model': "training",
                'default_name': "Formation - " + self.partner_id.name,
                'default_x_sinergis_calendar_event_client': self.partner_id.id, # Specificity for Sinergis
                'x_sinergis_calendar_event_contact': self.partner_manager_id.id, # Specificity for Sinergis
                'default_is_training': True,
                'default_training_id': self.id,
            }
            return action
        else:
            raise ValidationError("Veuillez entrer un client avant de planifier des heures")
    def send_invitation_participants(self):
        if Training.verifiation_fields(self):
            mail_count = 0
            for participant in self.training_participants:
                if not participant.invitation_sent:
                    TrainingParticipants.send_invitation_individual(participant)
                    mail_count += 1
            if mail_count == 0:
                raise ValidationError("Vous avez déjà envoyé l'invitation à tous les participants, si un des participants n'a pas reçu le mail, veuillez lui envoyer individuellement grace bouton situé sur sa ligne.")

    def send_diagnostic_quiz_participants (self):
        if Training.verifiation_fields(self):
            mail_count = 0
            for participant in self.training_participants:
                if not participant.diagnostic_quiz_sent:
                    TrainingParticipants.send_diagnostic_quiz_individual(participant)
                    mail_count += 1
            if mail_count == 0:
                raise ValidationError("Vous avez déjà envoyé le quiz de positionnement à tous les participants, si un des participants n'a pas reçu le mail, veuillez lui envoyer individuellement grace bouton situé sur sa ligne.")

    def download_training_evaluation (self):
        return self.env.ref('training.training_consultant_evaluation_report').report_action(self)

    def send_training_ended_participants (self):
        if not self.type_product_plan_id:
            raise ValidationError("Il vous faut un plan de formation pour envoyer les mails")
        mail_count = 0
        for participant in self.training_participants:
            if not participant.training_ended_sent:
                TrainingParticipants.send_training_ended_individual(participant)
                mail_count += 1
        if mail_count == 0:
                raise ValidationError("Vous avez déjà envoyé le mail à tous les participants, si un des participants ne l'a pas reçu, veuillez lui envoyer individuellement grace bouton situé sur sa ligne.")

    def send_delayed_assessment_client (self):
        if Training.verifiation_fields(self):
            if self.partner_manager_id:
                if self.partner_manager_id.email:
                    if not self.token_delayed_assessment:
                        self.token_delayed_assessment = "dela-"+str(self.id)+secrets.token_urlsafe(40)
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    template_id = self.env.ref('training.training_delayed_assessment_mail').id
                    self.env["mail.template"].browse(template_id).with_context(base_url=base_url).send_mail(self.id, force_send=True)
                    self.delayed_assessment_sent = True

    def send_opco_quiz (self):
        if Training.verifiation_fields(self):
            if self.opco_id:
                if self.opco_id.email:
                    if not self.token_opco_quiz:
                        self.token_opco_quiz = "dela-"+str(self.id)+secrets.token_urlsafe(40)
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    template_id = self.env.ref('training.training_opco_quiz_mail').id
                    self.env["mail.template"].browse(template_id).with_context(base_url=base_url).send_mail(self.id, force_send=True)
                    self.opco_quiz_sent = True
            else:
                raise ValidationError("Vous devez renseigner un OPCO (partie commerciale) afin d'envoyer le questionnaire OPCO")

    # def button_download_all_documents (self):
    #     path = os.path.dirname(os.path.realpath(__file__))
    #     with open(path+"/../static/src/zip/to_zip/signed_quote.pdf", "wb+") as binary_file:
    #         binary_file.write(base64.b64decode(self.signed_quote))
    #     with open(path+"/../static/src/zip/to_zip/signed_agreement.pdf", "wb+") as binary_file:
    #         binary_file.write(base64.b64decode(self.signed_agreement))
    #     with open(path+"/../static/src/zip/to_zip/signed_attendance_sheet.pdf", "wb+") as binary_file:
    #         binary_file.write(base64.b64decode(self.signed_attendance_sheet))
    #     shutil.make_archive(path+"/../static/src/zip/all_documents", 'zip', path+"/../static/src/zip/to_zip")

    #=======AUTOMATISATIONS=======

    def automating_closed_training (self):
        for rec in self:
            today = date.today()
            if (today - self.training_closed_date).days >= 30:
                if self.delayed_assessment_sent == False:
                    Training.send_delayed_assessment_client(self)
            if (today - self.training_closed_date).days >= 60:
                if self.opco_quiz_sent == False:
                    Training.send_opco_quiz(self)

    # =====QWEB FUNCTIONS=====
    # Function used to have all disability referent in remote and non remote invitation
    def get_disability_referents (self):
        return self.env['training.disability_referent'].sudo().search([])

class TrainingParticipants(models.Model):
    _name = "training.participants"
    _description = "Participants aux formations"

    training_id = fields.Many2one("training")
    training_state = fields.Selection(related="training_id.state")
    name = fields.Char(string="Nom")
    position = fields.Char(string="Fonction")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Téléphone")

    partner_contact_id = fields.Many2one("res.partner", string="Référence du contact")

    #Quiz tokens
    token_quiz_positioning = fields.Char(default="")
    token_quiz_diagnostic = fields.Char(default="")

    token_quiz_prior_learning = fields.Char(default="")
    token_quiz_training_evaluation = fields.Char(default="")

    #Consultant part
    invitation_sent = fields.Boolean(string="Invitation envoyée",default=False)
    diagnostic_quiz_sent = fields.Boolean(string="Quiz de positionnement envoyé",default=False)

    answer_positioning_quiz = fields.Html(default="",readonly=True, string="Réponse au quiz de diagnostic")
    mark_positioning_quiz = fields.Float(string="Note du quiz de diagnostic")
    positioning_quiz_received = fields.Boolean(string="Quiz de diagnostic reçu",default=False,compute="_compute_positioning_quiz_received")

    answer_quiz_diagnostic = fields.Html(default="",readonly=True, string="Réponse au quiz de positionnement")
    mark_quiz_diagnostic = fields.Float(string="Note du quiz de positionnement")
    diagnostic_received = fields.Boolean(string="Positionnement reçu",default=False,compute="_compute_diagnostic_received")

    #Training ended part
    is_rated = fields.Boolean(string="Évalué",default=False, compute="_compute_is_rated")
    evaluation_engagment_mark = fields.Selection([('A', 'A'),('B','B'),('C','C'),('D','D')], string="Note de l'engagement")
    training_end_mark = fields.Selection([('A', 'A'),('B','B'),('C','C'),('D','D')], string="Note compétences formation")

    training_ended_sent = fields.Boolean(string="Mail envoyé",default=False)
    answer_prior_learning_quiz = fields.Html(default="",readonly=True, string="Réponse au quiz d'évaluation des acquis")
    mark_prior_learning_quiz = fields.Float(string="Note du quiz d'évaluation des acquis")
    prior_learning_quiz_received = fields.Boolean(string="Quiz évaluation acquis reçu",default=False,compute="_compute_prior_learning_quiz_received")

    answer_training_evaluation = fields.Html(default="",readonly=True, string="Réponse au quiz d'évaluation de la formation")
    mark_training_evaluation = fields.Float(string="Note du quiz d'évaluation de la formation")
    training_evaluation_received = fields.Boolean(string="Quiz évaluation formation",default=False,compute="_compute_training_evaluation_received")

    @api.depends("is_rated")
    def _compute_is_rated (self):
        for rec in self:
            if rec.evaluation_engagment_mark and rec.training_end_mark:
                rec.is_rated = True
            else:
                rec.is_rated = False

    @api.depends('positioning_quiz_received')
    def _compute_positioning_quiz_received (self):
        for rec in self:
            if rec.answer_positioning_quiz:
                rec.positioning_quiz_received = True
            else:
                rec.positioning_quiz_received = False

    @api.depends('diagnostic_received')
    def _compute_diagnostic_received (self):
        for rec in self:
            if rec.answer_quiz_diagnostic:
                rec.diagnostic_received = True
            else:
                rec.diagnostic_received = False

    @api.depends('prior_learning_quiz_received')
    def _compute_prior_learning_quiz_received (self):
        for rec in self:
            if rec.answer_prior_learning_quiz:
                rec.prior_learning_quiz_received = True
            else:
                rec.prior_learning_quiz_received = False

    @api.depends('training_evaluation_received')
    def _compute_training_evaluation_received (self):
        for rec in self:
            if rec.answer_training_evaluation:
                rec.training_evaluation_received = True
            else:
                rec.training_evaluation_received = False

    @api.onchange("partner_contact_id")
    def on_change_partner_contact_id(self):
        self.name = self.partner_contact_id.name
        self.position = self.partner_contact_id.function
        self.email = self.partner_contact_id.email
        self.phone = self.partner_contact_id.phone

    def remove_participant (self):
        self.unlink()

    def send_invitation_individual(self):
        if Training.verifiation_fields(self.training_id):
            if not self.training_id.planned_hours_ids :
                raise ValidationError("Veuillez planifier des heures avant d'envoyer les invitations.")
            if not self.training_id.remote_learning:
                if self.training_id.location_selection == "other":
                    if not self.training_id.location_street or not self.training_id.location_city or not self.training_id.location_zip or not self.training_id.location_country_id:
                        raise ValidationError("Veuillez remplir entièrement l'adresse de localisation avant d'envoyer les invitations.")
            if self.email:
                #Create the diagnostic quiz token
                if not self.token_quiz_positioning:
                    self.token_quiz_positioning = "posi-"+str(self.id)+secrets.token_urlsafe(40)
                attach_obj = self.env['ir.attachment']
                attachment_ids = []
                result_binary = self.env['ir.config_parameter'].sudo().get_param('training.training_booklet')
                attach_data = {
                    'name': 'Livret de formation.pdf',
                    'datas': result_binary,
                    'res_model': 'ir.ui.view',
                }
                attach_id = attach_obj.create(attach_data)
                attachment_ids.append(attach_id.id)

                # Create iCalendar File
                timezone = pytz.timezone(self.env.user.tz)
                cal = Calendar()
                
                for line in self.training_id.planned_hours_ids.sorted(key=lambda x: x.start):
                    event = Event()
                    event.add('summary', f'Formation Sinergis : {self.training_id.course_title}')
                    event.add('dtstart', line.start.replace(tzinfo=timezone))
                    event.add('dtend', line.stop.replace(tzinfo=timezone))
                    event.add('dtstamp', line.start.replace(tzinfo=timezone))
                    if self.training_id.remote_learning :
                        location = ""
                        event.add('url', self.training_id.remote_learning_link)
                    else :
                        if self.training_id.location_selection == 'company':
                            location = "Agence Sinergis"
                        else :
                            if self.training_id.location_street2:
                                location = f"{self.training_id.location_street} {self.training_id.location_street2}, {self.training_id.location_zip} {self.training_id.location_city}, {self.training_id.location_country_id.name}"
                            else:
                                location = f"{self.training_id.location_street}, {self.training_id.location_zip} {self.training_id.location_city}, {self.training_id.location_country_id.name}"
                    event['location'] = location
                    cal.add_component(event)
                result_binary = base64.b64encode(cal.to_ical())
                attach_data = {
                    'name': 'Formation.ics',
                    'datas': result_binary,
                    'res_model': 'ir.ui.view',
                }
                attach_id = attach_obj.create(attach_data)
                attachment_ids.append(attach_id.id)

                values = {'attachment_ids':attachment_ids}
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                if self.training_id.remote_learning:
                    template_id = self.env.ref('training.training_invitation_mail_remote').id
                else :
                    template_id = self.env.ref('training.training_invitation_mail').id
                self.env["mail.template"].browse(template_id).with_context(base_url=base_url).send_mail(self.id, force_send=True,email_values=values)
                self.invitation_sent = True
            else :
                raise ValidationError("Ce participant n'a pas de mail, veuillez le renseigner en revenant à la partie commerciale.")

    def send_diagnostic_quiz_individual(self):
        if Training.verifiation_fields(self.training_id):
            if self.email:
                if not self.token_quiz_diagnostic:
                    self.token_quiz_diagnostic = "diag-"+str(self.id)+secrets.token_urlsafe(40)
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                template_id = self.env.ref('training.training_diagnostic_quiz_mail').id
                self.env["mail.template"].browse(template_id).with_context(base_url=base_url).send_mail(self.id, force_send=True)
                self.diagnostic_quiz_sent = True
            else :
                raise ValidationError("Ce participant n'a pas de mail, veuillez le renseigner en revenant à la partie commerciale.")

    def send_training_ended_individual(self):
        if self.training_id:
            if not self.training_id.type_product_plan_id:
                raise ValidationError("Il vous faut un plan de formation pour envoyer le mail")
            if self.email:
                if not self.token_quiz_prior_learning:
                    self.token_quiz_prior_learning = "prio-"+str(self.id)+secrets.token_urlsafe(40)
                if not self.token_quiz_training_evaluation:
                    self.token_quiz_training_evaluation = "eval-"+str(self.id)+secrets.token_urlsafe(40)
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                template_id = self.env.ref('training.training_ended_quiz_mail').id
                self.env["mail.template"].browse(template_id).with_context(base_url=base_url).send_mail(self.id, force_send=True)
                self.training_ended_sent = True
            else :
                raise ValidationError("Ce participant n'a pas de mail, veuillez le renseigner en revenant à la partie commerciale.")

    def open_participant_button (self):
        return {
            "name": "Participant",
            "type": "ir.actions.act_window",
            "res_model": "training.participants",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            }

#===TRAINING TYPE===

class TrainingType(models.Model):
    _name = "training.type"
    _description = "Type de formation"
    name = fields.Char(string="Nom",required=True)

class TrainingTypeProduct(models.Model):
    _name = "training.type.product"
    _description = "Produit concerné par la formation"
    type_id = fields.Many2one("training.type",string="Type de formation",required=True)
    name = fields.Char(string="Nom",required=True)

class TrainingTypeProductPlan(models.Model):
    _name = "training.type.product.plan"
    _description = "Plan de formation"
    type_id = fields.Many2one("training.type",string="Type de formation",required=True)
    product_id = fields.Many2one("training.type.product",string="Produit",required=True)
    name = fields.Char(string="Nom",required=True)
    training_plan_file = fields.Binary(string="Plan de formation (PDF)")

#===TRAINING LOCATION===
class TrainingLocation(models.Model):
    _name = "training.location"
    _description = "Localisation de la formation"
    name = fields.Char(string="Nom",required=True)

#===TRAINING LOACTION===
class TrainingOpco(models.Model):
    _name = "training.opco"
    _description = "Opérateurs de compétences"
    name = fields.Char(string="Nom",required=True)
    email = fields.Char(string="Email",required=True)

class TrainingAgreementInternalSigner (models.Model):
    _name="training.agreement_internal_signer"
    _description = "Signataires internes de la convention"
    _rec_name = "user_id"
    user_id = fields.Many2one("res.users",string='Signataire',required=True)
    company_id = fields.Many2one('res.company', string="Société Sinergis",required=True)
    signature = fields.Binary(string="Signature",required=True)

class TrainingDisabilityReferent (models.Model):
    _name="training.disability_referent"
    _description = "Référents handicape"
    _rec_name = "user_id"
    user_id = fields.Many2one("res.users",string='Référent',required=True)
    phone = fields.Char(string="Téléphone", required=True)
    mail =fields.Char(string="Email", required=True)


# Classe qui comporte les différentes feuilles d'émargement de la formation
class TrainingAttendanceSheet(models.Model):
        _name = "training.attendance_sheet"
        _description = "Feuilles d'émargement de la formation"

        training_id = fields.Many2one("training",string="Formation",required=True)

        name = fields.Char(string="Nom",required=True)
        file = fields.Binary(string="Feuille", required=True)


