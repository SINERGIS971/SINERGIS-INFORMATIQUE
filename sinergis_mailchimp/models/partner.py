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
        ids_to_update = []
        # Pagination data
        page_size = 500
        actual_page = 0
        total_page = 1 # Default page count is 1. Page count computed after reading the first page.
        print("Loading Mailchimp data ...")
        while actual_page <= total_page: 
            print(str(int(actual_page/total_page*100)) + ' %')
            try:
                response = mailchimp.lists.get_list_members_info(list_id,count=page_size,offset=actual_page*page_size)
                if 'members' in response:
                    for user in response['members']:
                        # email_list store existing email address
                        if user['email_address'] :
                            email_list.append(user['email_address'].lower()) # Lower email to don't have double email
                            
                            # Check and add a mailchimp_id
                            partner = self.env['res.partner'].sudo().search(['&','&',('email','=',user['email_address']),('is_company','=',False),('parent_id','!=',False)], limit=1)
                            if partner :
                                partner.mailchimp_id = user['id']
                        
                        # Check if user exists in database
                        odoo_user = self.env['res.partner'].sudo().search(['&','&',('mailchimp_id', '=', user['id']),('is_company','=',False),('parent_id','!=',False)], limit=1)
                        if odoo_user :
                            update = False
                            odoo_firstname = odoo_user.x_sinergis_societe_contact_firstname.replace(" ", "") if odoo_user.x_sinergis_societe_contact_firstname else ''
                            odoo_lastname = odoo_user.x_sinergis_societe_contact_lastname.replace(" ", "") if odoo_user.x_sinergis_societe_contact_lastname else ''
                            odoo_email = str(odoo_user.email).replace(" ", "")
                            
                            mailchimp_firstname = str(user['merge_fields']['FNAME']).replace(" ", "")
                            mailchimp_lastname = str(user['merge_fields']['LNAME']).replace(" ","")
                            mailchimp_email = str(user['email_address']).replace(" ", "")
                            
                            # Problem in Sinergis database
                            odoo_firstname = odoo_firstname.replace("<Nonrenseigné>","")
                            odoo_lastname = odoo_lastname.replace("<Nonrenseigné>","")
                            
                            if odoo_firstname != mailchimp_firstname:
                                print('FNAME CHANGE : ' + odoo_firstname + " | " + str(mailchimp_firstname))
                                update = True
                            if odoo_lastname != mailchimp_lastname:
                                print('LNAME CHANGE : ' + odoo_lastname + " | " + str(mailchimp_lastname))
                                update = True
                            if odoo_email != mailchimp_email:
                                print('EMAIL CHANGE : ' + odoo_email + " | " + str(mailchimp_email))
                                update = True
                            # If we need to update, add to ids_to_update array
                            if update:
                                ids_to_update.append(user['id'])
                    total_page = int(response['total_items'])//page_size
                actual_page += 1
            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))
                return

        print("Updating Mailchimp data ...")
        print("    Loading Odoo clients to create on Mailchimp ...")
        members = []
        partners = self.env['res.partner'].sudo().search(['&',('is_company','=',False),('parent_id','!=',False)], limit=100000)
        #print(str(id_to_update))

        for partner in partners:
            # Only partners with email
            if partner.email:
                # If email is in correct format and client is not actually in mailchimp
                partner_email = partner.email
                # Lower email to don't have double email
                if re.match(email_regex,partner_email) and partner_email.lower() not in email_list: # Verify if email format is correct and if not exists in mailchimp
                    print("Adding Mailchimp contact : " + partner_email)
                    email_list.append(partner_email)
                    
                    partner_firstname = partner.x_sinergis_societe_contact_firstname if partner.x_sinergis_societe_contact_firstname else ""
                    partner_lastname = partner.x_sinergis_societe_contact_lastname if partner.x_sinergis_societe_contact_lastname else ""
                    member_info = {
                                    "email_address": partner_email,
                                    "status": "subscribed",
                                    "merge_fields": {
                                        "FNAME": partner_firstname,
                                        "LNAME": partner_lastname
                                    }
                                  }
                    # Ajout du tag de la société
                    if partner.parent_id :
                        partner_company_tag = self.env['sinergis_mailchimp.settings.company.tag'].search([("company_id","=",partner.parent_id.company_id.id)])
                        if partner_company_tag:
                            member_info["tags"] = [partner_company_tag.name]
                    
                    members.append(member_info)
        
        print('New members count : ' + str(len(members)))
        print("    Sending new users to mailchimp ...")
        # Send data to Mailchimp
        for i in range(0, len(members)//200 + 1):
            print(str(int(i/(len(members)//200 + 1)*100)) + ' %')
            try:
                response = mailchimp.lists.batch_list_members(list_id, {'members': members[i*200:(i+1)*200]})
                print("response: {}".format(response))
                # Adding mailchimp_id to new members
                if "new_members" in response :
                    if len(response["new_members"]) > 0:
                        for new_member in response["new_members"]:
                            partner = self.env['res.partner'].sudo().search(['&',('email','=',new_member['email_address']),('is_company','=',False),('parent_id','!=',False)], limit=1)
                            if partner :
                                #print("ADDING MAILCHIMP_ID TO NEW CLIENT")
                                partner.mailchimp_id = new_member['id']
            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))
                
        print("    Sending users updates to mailchimp ...")
        return True
        if ids_to_update:
            for id_to_update in ids_to_update :
                partner = self.env['res.partner'].sudo().search([('is_company','=',False),('mailchimp_id','=',id_to_update)],limit=1)
                partner_firstname = partner.x_sinergis_societe_contact_firstname if partner.x_sinergis_societe_contact_firstname else ""
                partner_lastname = partner.x_sinergis_societe_contact_lastname if partner.x_sinergis_societe_contact_lastname else ""

                #Sinergis database problem
                partner_firstname = partner_firstname.replace("<Non renseigné>","")
                partner_lastname = partner_lastname.replace("<Non renseigné>","")

                partner_email = partner.email
                if partner_email :
                    print(f"Mailchimp update of {partner_firstname} {partner_lastname}")
                    member_info = {
                                    "email_address": partner_email,
                                    "merge_fields": {
                                    "FNAME": partner_firstname,
                                    "LNAME": partner_lastname    
                                    }
                                }
                    try:
                        mailchimp.lists.update_list_member(list_id, partner.mailchimp_id, member_info)
                    except ApiClientError as error:
                        print("An exception occurred: {}".format(error.text))
            
                        