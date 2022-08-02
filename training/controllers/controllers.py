# -*- coding: utf-8 -*-
from odoo import http
import re


class Training(http.Controller):
    @http.route('/training/training', auth='public', methods=['GET'])
    def index(self, **kw):
        token = kw.get("token")
        if not token:
            return ("Vous n'avez pas accès à cette page, veuillez contacter Sinergis.")
        TrainingParticipant = http.request.env['training.participants']
        participant = TrainingParticipant.search(['|','|','|',('token_quiz_diagnostic', '=', token ),('token_quiz_positioning', '=', token ),('token_quiz_prior_learning', '=', token ),('token_quiz_training_evaluation', '=', token )])
        training = http.request.env['training'].search(['|',('token_delayed_assessment', '=', token ),('token_opco_quiz', '=', token )])
        if not participant and not training:
            return ("Nous n'avions pas réussi à vous authentifier, veuillez contacter Sinergis.")
        #Vérification du type de quiz
        TrainingQuiz = http.request.env['training.quiz']
        if participant:
            training_id = participant.training_id
            training_plan_id = participant.training_id.type_product_plan_id
        elif training:
            training_id = training
            training_plan_id = training_id.type_product_plan_id

        if participant:
            if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
                if participant.answer_quiz_diagnostic:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.search([('training_type_product_plan', '=', training_plan_id.id),('quiz_type', '=', 'diagnostic')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.name,
                            "user_name" : participant.name,
                            "quiz" : training_quiz
                        })
                    else:
                        return("Il n'y a pas de quiz associé à cette étape de la formation")
                else:
                    return("Il n'y a pas de plan associé à cette formation, veuillez contacter Sinergis.")
            elif participant.token_quiz_positioning == token: #C'est un quiz de positionnement
                if participant.answer_positioning_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.search([('training_type_product_plan', '=', training_plan_id.id),('quiz_type', '=', 'positioning')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.name,
                            "user_name" : participant.name,
                            "quiz" : training_quiz
                        })
                    else:
                        return("Il n'y a pas de quiz associé à cette étape de la formation")
                else:
                    return("Il n'y a pas de plan associé à cette formation, veuillez contacter Sinergis.")
            elif participant.token_quiz_prior_learning == token: #C'est un quiz de validation des acquis
                if participant.answer_prior_learning_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.search([('training_type_product_plan', '=', training_plan_id.id),('quiz_type', '=', 'prior_learning')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.name,
                            "user_name" : participant.name,
                            "quiz" : training_quiz
                        })
                    else:
                        return("Il n'y a pas de quiz associé à cette étape de la formation")
                else:
                    return("Il n'y a pas de plan associé à cette formation, veuillez contacter Sinergis.")
            elif participant.token_quiz_training_evaluation == token: #C'est un quiz d'évaluation de la formation
                if participant.answer_training_evaluation:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                training_quiz = TrainingQuiz.search([('quiz_type', '=', 'training_evaluation')])
                if training_quiz:
                    return http.request.render("training.quiz_page", {
                        "token" : token,
                        "company_name" : training_id.partner_id.name,
                        "user_name" : participant.name,
                        "quiz" : training_quiz
                    })
                else:
                    return("Il n'y a pas de quiz d'évaluation de formation sur le serveur.")
        elif training:
            if training.token_delayed_assessment == token: #C'est un quiz à froid du client
                if training.answer_delayed_assessment:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.search([('quiz_type', '=', 'delayed_assessment')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.name,
                            "user_name" : training.partner_manager_id.name,
                            "quiz" : training_quiz
                        })
                    else:
                        return("Il n'y a pas de quiz associé à cette étape de la formation")
                else:
                    return("Il n'y a pas de plan associé à cette formation, veuillez contacter Sinergis.")
            elif training.token_opco_quiz == token: #C'est un quiz OPCO
                if training.answer_opco_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.search([('quiz_type', '=', 'opco')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.name,
                            "user_name" : training.partner_manager_id.name,
                            "quiz" : training_quiz
                        })
                    else:
                        return("Il n'y a pas de quiz associé à cette étape de la formation")
                else:
                    return("Il n'y a pas de plan associé à cette formation, veuillez contacter Sinergis.")


    @http.route('/training/training', auth='public', methods=['POST'],csrf=False)
    def index_post(self, **kw):
        if not 'token' in kw.keys():
            return("Token invalide")
        token = kw["token"]
        del kw["token"]
        TrainingParticipant = http.request.env['training.participants']
        participant = TrainingParticipant.search(['|','|','|',('token_quiz_diagnostic', '=', token ),('token_quiz_positioning', '=', token ),('token_quiz_prior_learning', '=', token ),('token_quiz_training_evaluation', '=', token)])
        training = http.request.env['training'].search(['|',('token_delayed_assessment', '=', token ),('token_opco_quiz', '=', token )])
        if not participant and not training:
            return ("Token invalide")

        questions = []
        questions_name = []
        questions_answer = list(kw.values())
        if participant:
            if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
                if participant.answer_quiz_diagnostic:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })

            if participant.token_quiz_positioning == token: #C'est un quiz diagnostic
                if participant.answer_positioning_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })

            if participant.token_quiz_prior_learning == token: #C'est un quiz d'évaluation des acquis
                if participant.answer_prior_learning_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })

            if participant.token_quiz_training_evaluation == token: #C'est un quiz d'évaluation de la formation
                if participant.answer_training_evaluation:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
        if training:
            if training.token_delayed_assessment == token: #C'est un quiz diagnostic
                if training.answer_delayed_assessment:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
            if training.token_opco_quiz == token: #C'est un quiz diagnostic
                if training.answer_opco_quiz:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
        questions = http.request.env['training.quiz.questions'].search([('id', '=', list(kw.keys()))])
        i = 0
        for question in questions:
            if question.type == "note1":
                questions_answer[i] = questions_answer[i] + " sur 5"
            questions_name.append(question.name)
            i += 1

        if (len(questions_name) != len(questions_answer)):
            return("Une erreur est survenue, merci de contacter Sinergis")
        n = len(questions_name)

        #Construction de la réponse
        TAG_RE = re.compile(r'<[^>]+>') #Retirer les balises des réponses
        body = "<table style='border-collapse: collapse;border: 1px solid;'><tr><th style='width:50%;border: 1px solid;'>Question</th><th style='border: 1px solid;'>Réponse</th></tr>"
        for i in range(0,n):
            questions_answer[i] = TAG_RE.sub('', questions_answer[i])
            body += "<tr style='margin-top:10px;'><td style='border: 1px solid;'>"+questions_name[i]+"</td><td style='border: 1px solid;'>"+questions_answer[i]+"</td></tr>"
        body+="</table>"

        if participant: #Si c'est une réponse d'un participant
            if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
                participant.answer_quiz_diagnostic = body
            elif participant.token_quiz_positioning == token: #C'est un quiz de positionnement
                participant.answer_positioning_quiz = body
            if participant.token_quiz_prior_learning == token: #C'est un quiz d'évaluation des acquis
                participant.answer_prior_learning_quiz = body
            if participant.token_quiz_training_evaluation == token: #C'est un quiz d'évaluation de la formation
                participant.answer_training_evaluation = body
        if training: #Si c'est une réponse du client
            if training.token_delayed_assessment == token: #C'est un quiz diagnostic
                training.answer_delayed_assessment = body
            if training.token_opco_quiz == token: #C'est un quiz opco
                training.answer_opco_quiz = body


        return http.request.render("training.quiz_page_message", {
            "message": "Merci pour votre participation !"
        })


        #mobile = ResPartner.search([('name', '=', 'Test' )]).mobile
        #quiz = http.request.env['training.quiz'].sudo().search([('name', '=', 'Quiz SAGE 100')])
        #return http.request.render("training.quiz_page", {
        #    "quiz" : quiz
        #})