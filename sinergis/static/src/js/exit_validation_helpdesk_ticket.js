odoo.define('sinergis.FormLeaveCheck', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const Dialog = require('web.Dialog');

    FormController.include({

        on_detach_callback: function () {
            const record = this.model.get(this.handle);

            if (record && record.model === 'helpdesk.ticket') {
                //const time = record.data.x_sinergis_helpdesk_ticket_temps_passe;
                const deducted = record.data.x_sinergis_helpdesk_ticket_is_facturee;
                const billing_type = record.data.x_sinergis_helpdesk_ticket_facturation;
                const hours_contract = record.data.x_sinergis_helpdesk_ticket_tache2;

                if (!deducted && (billing_type=="Contrat heures" || billing_type=="Devis")) {
                    new Dialog(this, {
                        title: 'Attention',
                        size: 'medium',
                        $content: $('<div>', {
                            html: "Vous venez de quitter un ticket sans décompter d'heures sur la tâche ! "
                        }),
                        buttons: [{
                            text: 'OK',
                            close: true,
                        }]
                    }).open();
                }
                if (billing_type=="Contrat heures" && !hours_contract) {
                    new Dialog(this, {
                        title: 'Attention',
                        size: 'medium',
                        $content: $('<div>', {
                            html: "Aucun contrat d'heures n'est rattaché à au ticket que vous venez de quitter !"
                        }),
                        buttons: [{
                            text: 'OK',
                            close: true,
                        }]
                    }).open();
                }
            } else if (record && record.model === 'calendar.event') {
                //const time = record.data.x_sinergis_calendar_duree_facturee;
                const deducted = record.data.x_sinergis_calendar_event_is_facturee;
                const billing_type = record.data.x_sinergis_calendar_event_facturation;
                const hours_contract = record.data.x_sinergis_calendar_event_tache2;

                if (!deducted && (billing_type=="Contrat heure" || billing_type=="Devis")) {
                    new Dialog(this, {
                        title: 'Attention',
                        size: 'medium',
                        $content: $('<div>', {
                            html: "Vous venez de quitter un évènement sans décompter d'heures sur la tâche ! "
                        }),
                        buttons: [{
                            text: 'OK',
                            close: true,
                        }]
                    }).open();
                }
                if (billing_type=="Contrat heure" && !hours_contract) {
                    new Dialog(this, {
                        title: 'Attention',
                        size: 'medium',
                        $content: $('<div>', {
                            html: "Aucun contrat d'heures n'est rattaché à l'évènement que vous venez de quitter !"
                        }),
                        buttons: [{
                            text: 'OK',
                            close: true,
                        }]
                    }).open();
                }
            }
            return this._super.apply(this, arguments);
        },
    });

});
