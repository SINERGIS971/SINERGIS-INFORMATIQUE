from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    @api.onchange("quiz_type")
    def on_change_quiz_type(self):
        if self.quiz_type == "training_evaluation" or self.quiz_type == "delayed_assessment" or self.quiz_type == "opco":
            self.training_type_id = False
            self.training_type_product = False
            self.training_type_product_plan = False
            if self.quiz_type == "training_evaluation":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'training_evaluation')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation des formations. Veuillez le supprimer afin d'en réaffecter un nouveau.")
            if self.quiz_type == "delayed_assessment":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'delayed_assessment')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation à froid. Veuillez le supprimer afin d'en réaffecter un nouveau.")
            if self.quiz_type == "opco":
                if self.env['training.quiz'].search_count([('quiz_type', '=', 'opco')]) >= 1:
                    self.quiz_type = False
                    raise ValidationError("Vous avez déjà un quiz attribué à l'évaluation des OPCO. Veuillez le supprimer afin d'en réaffecter un nouveau.")


class TrainingQuizQuestions(models.Model):
    _name = "training.quiz.questions"
    _description = "Questions Quiz"
    name = fields.Char(string="Question")
    quiz_id = fields.Many2one("training.quiz")
    type = fields.Selection([ ('text1', 'Texte court'),('text2', 'Texte long'),('note1', 'Note sur 5'),('multiple_choice', 'Choix multiple')], string="Type de question" )
    #Pour les réponses à choix multiple
    choice_ids = fields.One2many("training.quiz.questions.multiple_choice","question_id",string="Réponses possibles")

    required = fields.Boolean(string="Requis",default=False)

class TrainingQuizQuestionsMultipleChoice(models.Model):
    _name = "training.quiz.questions.multiple_choice"
    _description = "Questions à choix multiple"
    name = fields.Char(string="Choix")
    question_id = fields.Many2one("training.quiz.questions", string="")
    count = fields.Integer(string="Nombre de sélections", readonly=True, default=0)
