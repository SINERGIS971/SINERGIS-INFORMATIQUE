# -*- coding: utf-8 -*-
from odoo import http
import re
from datetime import date




class Training(http.Controller):
    @http.route('/training/training', auth='public', methods=['GET'])
    def index(self, **kw):
        token = kw.get("token")
        if not token:
            return ("Vous n'avez pas accès à cette page, veuillez contacter Sinergis.")
        TrainingParticipant = http.request.env['training.participants']
        participant = TrainingParticipant.sudo().search(['|','|','|',('token_quiz_diagnostic', '=', token ),('token_quiz_positioning', '=', token ),('token_quiz_prior_learning', '=', token ),('token_quiz_training_evaluation', '=', token )])
        training = http.request.env['training'].sudo().search(['|',('token_delayed_assessment', '=', token ),('token_opco_quiz', '=', token )])
        if not participant and not training:
            return ("Nous n'avions pas réussi à vous authentifier, veuillez contacter Sinergis.")
        #Vérification du type de quiz
        TrainingQuiz = http.request.env['training.quiz']
        if participant:  # Si plusieurs participants peuvent accéder au même quiz
            training_id = participant.training_id
            training_plan_id = participant.training_id.type_product_plan_id
        elif training:  # Si c'est un quiz de formation non destiné à chaque participant
            training_id = training
            training_plan_id = training_id.type_product_plan_id

        if participant:
            if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
                if participant.answer_quiz_diagnostic:
                    return http.request.render("training.quiz_page_message", {
                        "message": "Vous avez déjà rempli ce questionnaire"
                    })
                if training_plan_id:
                    training_quiz = TrainingQuiz.sudo().search([('training_type_product_plan', '=', training_plan_id.id),('quiz_type', '=', 'diagnostic')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.sudo().name,
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
                    training_quiz = TrainingQuiz.sudo().search([('quiz_type', '=', 'positioning')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.sudo().name,
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
                    training_quiz = TrainingQuiz.sudo().search([('training_type_product_plan', '=', training_plan_id.id),('quiz_type', '=', 'prior_learning')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.sudo().name,
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
                training_quiz = TrainingQuiz.sudo().search([('quiz_type', '=', 'training_evaluation')])
                if training_quiz:
                    return http.request.render("training.quiz_page", {
                        "token" : token,
                        "company_name" : training_id.partner_id.sudo().name,
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
                    training_quiz = TrainingQuiz.sudo().search([('quiz_type', '=', 'delayed_assessment')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.sudo().name,
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
                    training_quiz = TrainingQuiz.sudo().search([('quiz_type', '=', 'opco')])
                    if training_quiz:
                        return http.request.render("training.quiz_page", {
                            "token" : token,
                            "company_name" : training_id.partner_id.sudo().name,
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
        participant = TrainingParticipant.sudo().search(['|','|','|',('token_quiz_diagnostic', '=', token ),('token_quiz_positioning', '=', token ),('token_quiz_prior_learning', '=', token ),('token_quiz_training_evaluation', '=', token)])
        if not participant :
            training = http.request.env['training'].sudo().search(['|',('token_delayed_assessment', '=', token ),('token_opco_quiz', '=', token )])
        else :
            training = participant.training_id
        if not training:
            return ("Token invalide")

        questions = []
        
        question_data = kw
        questions_name = []
        questions_answer = []
        
        quiz_type=False
        if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
            quiz_type="diagnostic"
            if participant.answer_quiz_diagnostic:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        elif participant.token_quiz_positioning == token: #C'est un quiz positionnement
            quiz_type="positioning"
            if participant.answer_positioning_quiz:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        elif participant.token_quiz_prior_learning == token: #C'est un quiz d'évaluation des acquis
            quiz_type="prior_learning"
            if participant.answer_prior_learning_quiz:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        elif participant.token_quiz_training_evaluation == token: #C'est un quiz d'évaluation de la formation
            quiz_type="training_evaluation"
            if participant.answer_training_evaluation:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        elif training.token_delayed_assessment == token: #C'est un quiz diagnostic
            quiz_type="delayed_assessment"
            if training.answer_delayed_assessment:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        elif training.token_opco_quiz == token: #C'est un quiz diagnostic
            quiz_type="opco"
            if training.answer_opco_quiz:
                return http.request.render("training.quiz_page_message", {
                    "message": "Vous avez déjà rempli ce questionnaire"
                })
        if not quiz_type:
            return ("Il n'y a pas de quiz associé, veuillez contacter un administrateur système.")
        if quiz_type == "opco" or quiz_type == "delayed_assessment" or quiz_type == "training_evaluation" or quiz_type == "positioning":
            quiz = http.request.env['training.quiz'].sudo().search([('quiz_type', '=', quiz_type)])
        else:
            quiz = http.request.env['training.quiz'].sudo().search(['&',('training_type_product_plan', '=', training.type_product_plan_id.id),('quiz_type', '=', quiz_type)])
        questions = http.request.env['training.quiz.questions'].sudo().search([('quiz_id', '=', quiz.id)])
        #Score variables
        total_answers = 0
        right_answers = 0

        for question in questions:
            questions_name.append(question.name)
            if str(question.id) in question_data:
                answer = question_data[str(question.id)]
            else:
                answer = ""
            if question.type == "note1":
                if answer != "" :
                    rate = int(answer)
                    vals = {'rate': rate,
                            'question_id': question.id
                            }
                    http.request.env['training.quiz.questions.rate.record'].sudo().create(vals)
                    questions_answer.append(answer + " sur 5")
                else : 
                    questions_answer.append("")
            #Si c'est une question à choix multiple
            elif question.type == "multiple_choice":
                question_right_answers = http.request.env['training.quiz.questions.multiple_choice'].sudo().search(['&',('question_id', '=',question.id),('right_answer','=',True)])
                if question_right_answers :  # If question have right answer
                    total_answers += 1  # Increment the number of rated answers answered
                    
                question_choice = http.request.env['training.quiz.questions.multiple_choice'].sudo().search(['&',('question_id', '=',question.id),('name','=',answer)])
                if question_choice:
                    vals = {'date': date.today(),
                            'multiple_choice_id': question_choice.id
                            }
                    http.request.env['training.quiz.questions.multiple_choice.record'].sudo().create(vals)
                    if question_choice.right_answer == True :
                        right_answers += 1  # If it's a good answer : Add 1 to score
                questions_answer.append(answer)
            else:
                questions_answer.append(answer)

        if (len(questions_name) != len(questions_answer)):
            return("Une erreur est survenue, merci de contacter Sinergis")
        n = len(questions_name)

        #Construction de la réponse
        TAG_RE = re.compile(r'<[^>]+>') #Retirer les balises des réponses
        body = ""
        mark = -1
        if total_answers != 0 :  # If the quiz have rated answers
            mark = right_answers/total_answers * 20
        mark = float("{:.2f}".format(mark)) # Limit to 2 digits
        body += "<table style='border-collapse: collapse;border: 1px solid;'><tr><th style='width:50%;border: 1px solid; padding:2px;'>Question</th><th style='width:50%;border: 1px solid;padding:2px;'>Réponse</th></tr>"
        for i in range(0,len(questions_answer)):
            questions_answer[i] = TAG_RE.sub('', questions_answer[i])
            body += "<tr style='margin-top:10px;'><td style='border: 1px solid;padding:2px;width:50%;'>"+questions_name[i]+"</td><td style='border: 1px solid;padding:2px;width:50%;'>"+questions_answer[i]+"</td></tr>"
        body+="</table>"

        if participant: #Si c'est une réponse d'un participant
            if participant.token_quiz_diagnostic == token: #C'est un quiz diagnostic
                participant.answer_quiz_diagnostic = body
                participant.mark_quiz_diagnostic = mark
            elif participant.token_quiz_positioning == token: #C'est un quiz de positionnement
                participant.answer_positioning_quiz = body
                participant.mark_positioning_quiz = mark
            if participant.token_quiz_prior_learning == token: #C'est un quiz d'évaluation des acquis
                participant.answer_prior_learning_quiz = body
                participant.mark_prior_learning_quiz = mark
            if participant.token_quiz_training_evaluation == token: #C'est un quiz d'évaluation de la formation
                participant.answer_training_evaluation = body
                participant.mark_training_evaluation = mark
        if training: #Si c'est une réponse du client
            if training.token_delayed_assessment == token: #C'est un quiz diagnostic
                training.answer_delayed_assessment = body
                training.mark_delayed_assessment = mark
            if training.token_opco_quiz == token: #C'est un quiz opco
                training.answer_opco_quiz = body
                training.mark_opco_quiz = mark


        return http.request.render("training.quiz_page_message", {
            "message": "Merci pour votre participation !"
        })


        #mobile = ResPartner.search([('name', '=', 'Test' )]).mobile
        #quiz = http.request.env['training.quiz'].sudo().search([('name', '=', 'Quiz SAGE 100')])
        #return http.request.render("training.quiz_page", {
        #    "quiz" : quiz
        #})



