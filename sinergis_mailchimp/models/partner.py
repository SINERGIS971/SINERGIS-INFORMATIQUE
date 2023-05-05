# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

class ResPartner(models.Model):

    _inherit = "res.partner"

    def sync_mailchimp(self):
        #TODO : LOAS API KEY AND LIST ID
        api_key = "c6f7b99fe8038715aece784eeb92c87b-us21"
        list_id = "98726319a6"
        mailchimp = MailchimpMarketing.Client()
        mailchimp.set_config({
        "api_key": api_key,
        "server": api_key.split("-")[1]
        })
        # Load Mailchimp data
        email_list = []
        try:
            response = mailchimp.lists.get_list_members_info(list_id)
            print("response: {}".format(response))
            if 'members' in response:
                for user in response['members']:
                    if user['email_address'] :
                        email_list.append(user['email_address'])
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))
            return
        partners = self.env['res.partner'].search([('employee','=',True)])
        for partner in partners:
            # Only partners with email
            if partner.email:
                if partner.email not in email_list:
                    member_info = {
                                    "email_address": partner.email,
                                    "status": "subscribed",
                                    "merge_fields": {
                                        "FNAME": partner.x_sinergis_societe_contact_firstname,
                                        "LNAME": partner.x_sinergis_societe_contact_lastname
                                    }
                                  }
                    try:
                        response = mailchimp.lists.add_list_member(list_id, member_info)
                        print("response: {}".format(response))
                    except ApiClientError as error:
                        print("An exception occurred: {}".format(error.text))



