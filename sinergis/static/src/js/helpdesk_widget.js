odoo.define('sinergis.SetPartnerReminder', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var web_client = require('web.web_client');
    
    var _t = core._t;
    
    var SinergisSetPartnerReminder = AbstractAction.extend({
        template: "SetPartnerReminder",
    
        start: function () {
            var self = this;
            web_client.set_title('Sélectionnez une date et une heure');
            var $button = self.$('.oe_form_button');
            $button.appendTo(this.getParent().$footer);
            $button.eq(1).click(function () {
                self.$el.parents('.modal').modal('hide');
            });
            $button.eq(0).click(function () {
                self._rpc({
                        route: '/web/session/change_sinergis_password',
                        params: {
                            fields: $('form[name=datetime_reminder]').serializeArray()
                        }
                    })
                    .then(function (result) {
                        if (result.error) {
                            self.displayNotification({
                                message: result.error,
                                type: 'danger'
                            });
                        } else {
                            self.displayNotification({
                                message: _t("Relance client enregistrée"),
                                type: 'success',
                            });
                        }
                    });
            });
        },
    });
    
    core.action_registry.add("sinergis_set_partner_reminder", SinergisSetPartnerReminder);
    
    return SinergisChangePassword;
    
    });
    