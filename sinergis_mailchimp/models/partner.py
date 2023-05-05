# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

import mailchimp_marketing as MailchimpMarketing
import re

from mailchimp_marketing.api_client import ApiClientError

class ResPartner(models.Model):

    _inherit = "res.partner"

    mailchimp_id = fields.Char(string="Mailchimp ID")

    def sync_mailchimp(self):
        # Loading API KEY and LIST ID from parameters
        api_key = self.env['ir.config_parameter'].sudo().get_param('sinergis_mailchimp.api_key')
        list_id = self.env['ir.config_parameter'].sudo().get_param('sinergis_mailchimp.list_id')
        if not api_key or not list_id :
            return
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b' # Regex verification for email
        # Connection to Mailchimp
        mailchimp = MailchimpMarketing.Client()
        mailchimp.set_config({
        "api_key": api_key,
        "server": api_key.split("-")[1]
        })
        email_list = [] # Actual emails on Mailchimp
        id_to_update = []
        # Pagination data
        page_size = 300
        actual_page = 0
        total_page = 1 # Default page count is 1. Page count computed after reading the first page.
        print("Loading Mailchimp data ...")
        while actual_page <= total_page: 
            try:
                response = mailchimp.lists.get_list_members_info(list_id,count=page_size,offset=actual_page*page_size)
                if 'members' in response:
                    for user in response['members']:
                        if user['email_address'] :
                            email_list.append(user['email_address'])

                        # Check if user exists in database
                        odoo_user = self.env['res.partner'].sudo().search([('mailchimp_id', '=', user['id'])], limit=1)
                        if odoo_user :
                            update = False
                            if odoo_user.x_sinergis_societe_contact_firstname != user['merge_fields']['FNAME']:
                                update = True
                            if odoo_user.x_sinergis_societe_contact_lastname != user['merge_fields']['LNAME']:
                                update = True
                            if str(odoo_user.email) != user['email_address']:
                                update = True
                            # If we need to update, add to id_to_update array
                            if update:
                                id_to_update.append(user['id'])
                    total_page = int(response['total_items'])//page_size
                actual_page += 1
            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))
                return
            
        partners = self.env['res.partner'].sudo().search([('is_company','=',False)])
        print(str(id_to_update))

        for partner in partners:
            # Only partners with email
            if partner.email:
                # If email is in correct format and client is not actually in mailchimp
                partner_email = partner.email
                if re.match(email_regex,partner_email) and partner_email not in email_list: # Verify if email format is correct and if not exists in mailchimp
                    print("Adding Mailchimp contact : " + partner_email)
                    member_info = {
                                    "email_address": partner_email,
                                    "status": "subscribed",
                                    "merge_fields": {
                                        "FNAME": partner.x_sinergis_societe_contact_firstname if partner.x_sinergis_societe_contact_firstname else "",
                                        "LNAME": partner.x_sinergis_societe_contact_lastname if partner.x_sinergis_societe_contact_lastname else ""
                                    }
                                  }
                    try:
                        response = mailchimp.lists.add_list_member(list_id, member_info)
                        # Update mailchimp id of partner :
                        partner.mailchimp_id = response['id']
                        print("response: {}".format(response))
                    except ApiClientError as error:
                        print("An exception occurred: {}".format(error.text))
                        