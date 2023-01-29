from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class TrainingQuiz(models.Model):
    _name = "training.quiz"
    _description = "Quiz"
    name = fields.Char(string="Nom du quiz")
    questions_ids = fields.One2many("training.quiz.questions","quiz_id", string="Questions")
    training_type_id = fields.Many2one("training.type", string="Type de formation")
    training_type_product = fields.Many2one("training.type.product", string="Produit")
    training_type_product_plan = fields.Many2one("training.type.product.plan",string="Plan de formation")
    quiz_type = fields.Selection([('positioning', 'Positionnement'),('diagnostic', 'Diagnostic'),('prior_learning', 'Évaluation des acquis'),('training_evaluation', 'Évaluation de la formation'),('delayed_assessment', 'Évaluation à froid du client'),('opco', "Quiz de l'OPCO")],required="True")

    @api.onchange("training_type_id")
    def on_change_type_id(self):
        self.training_type_product = False
        self.training_type_product_plan = False

    @api.onchange("training_type_product")
    def on_change_type_product_id(self):
        self.training_type_product_plan = False

    @api.onchange("training_type_product_plan")
    def on_change_training_type_product_plan (self):
        if self.env['training.quiz'].search_count([('quiz_type', '=', self.quiz_type), ('training_type_product_plan', '=', self.training_type_product_plan.id)]) >= 1:
            self.quiz_type = False
            raise ValidationError("Vous avez déjà un quiz attribué à cette formation avec le même type. Veuillez le supprimer afin d'en réaffecter un nouveau.")

    @api.onchange("quiz_type")
    def on_change_quiz_type(self):
        if self.quiz_type == "positioning" or self.quiz_type == "training_evaluation" or self.quiz_type == "delayed_assessment" or self.quiz_type == "opco":
            self.training_type_id = False
            self.training_type_product = False
            self.training_type_product_plan = False
            if self.quiz_type == "positioning":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'positioning')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué au positionnement. Veuillez le supprimer afin d'en réaffecter un nouveau.")
            elif self.quiz_type == "training_evaluation":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'training_evaluation')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation des formations. Veuillez le supprimer afin d'en réaffecter un nouveau.")
            elif self.quiz_type == "delayed_assessment":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'delayed_assessment')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation à froid. Veuillez le supprimer afin d'en réaffecter un nouveau.")
            elif self.quiz_type == "opco":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'opco')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation des OPCO. Veuillez le supprimer afin d'en réaffecter un nouveau.")
        else :
            if self.env['training.quiz'].search_count([('quiz_type', '=', self.quiz_type), ('training_type_product_plan', '=', self.training_type_product_plan.id)]) >= 1:
                self.quiz_type = False
                raise ValidationError("Vous avez déjà un quiz attribué à cette formation avec le même type. Veuillez le supprimer afin d'en réaffecter un nouveau.")



class TrainingQuizQuestions(models.Model):
    _name = "training.quiz.questions"
    _description = "Questions Quiz"
    name = fields.Char(string="Question")
    quiz_id = fields.Many2one("training.quiz")
    type = fields.Selection([ ('text1', 'Texte court'),('text2', 'Texte long'),('note1', 'Note sur 5'),('multiple_choice', 'Choix multiple')], string="Type de question" )
    #Pour les réponses à choix multiple
    choice_ids = fields.One2many("training.quiz.questions.multiple_choice","question_id",string="Réponses possibles")

    required = fields.Boolean(string="Requis",default=False)

    put_title = fields.Boolean(string="Mettre un titre de partie au dessus ?", default=False)
    title = fields.Char(string="Titre de partie")

    average_rate = fields.Float(string="Note moyenne", compute="_compute_average_rate")

    # -1 if no exists
    @api.depends("average_rate")
    def _compute_average_rate (self):
        for rec in self:
            if rec.type == "note1":
                elements = self.env['training.quiz.questions.rate.record'].sudo().search([('question_id', '=', rec.id)])
                n = len(elements)
                if n > 0:
                    s = 0
                    for element in elements:
                        s += element.rate
                    rec.average_rate = s/n
                else :
                    rec.average_rate = -1
            else :
                rec.average_rate = -1

class TrainingQuizQuestionsMultipleChoice(models.Model):
    _name = "training.quiz.questions.multiple_choice"
    _description = "Questions à choix multiple"
    name = fields.Char(string="Choix")
    question_id = fields.Many2one("training.quiz.questions", string="")
    right_answer = fields.Boolean(string="Bonne réponse ?", default = False)
    actual_month_count = fields.Integer(string="Sélections ce mois", compute="_compute_actual_month_count")
    last_month_count = fields.Integer(string="Sélections le mois dernier", compute="_compute_last_month_count")
    actual_year_count = fields.Integer(string="Sélections cette année", compute="_compute_actual_year_count")

    @api.depends("actual_month_count")
    def _compute_actual_month_count (self):
        for rec in self:
            rec.actual_month_count = self.env['training.quiz.questions.multiple_choice.record'].search_count([('multiple_choice_id', '=', rec.id),('date','<',(date.today()+relativedelta(months=1)).replace(day=1)),('date','>=',(date.today()).replace(day=1))])

    @api.depends("last_month_count")
    def _compute_last_month_count (self):
        for rec in self:
            rec.last_month_count = self.env['training.quiz.questions.multiple_choice.record'].search_count([('multiple_choice_id', '=', rec.id),('date','>=',(date.today()-relativedelta(months=1)).replace(day=1)),('date','<',(date.today()).replace(day=1))])

    @api.depends("actual_year_count")
    def _compute_actual_year_count (self):
        for rec in self:
            rec.actual_year_count = self.env['training.quiz.questions.multiple_choice.record'].search_count([('multiple_choice_id', '=', rec.id),('date','<',(date.today()+relativedelta(years=1)).replace(day=1,month=1)),('date','>=',(date.today()).replace(day=1,month=1))])

class TrainingQuizQuestionsRateRecord(models.Model):
    _name = "training.quiz.questions.rate.record"
    _description = "Réponse à une question notée"
    rate = fields.Integer(string="Note")
    question_id = fields.Many2one("training.quiz.questions", string="",readonly=True)

class TrainingQuizQuestionsMultipleChoiceRecord(models.Model):
    _name = "training.quiz.questions.multiple_choice.record"
    _description = "Réponse à une question à choix multiple"
    date = fields.Date(string="",readonly=True)
    multiple_choice_id = fields.Many2one("training.quiz.questions.multiple_choice", string="",readonly=True)
