odoo.define('sinergis.SinergisChangePassword', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var web_client = require('web.web_client');
    
    var _t = core._t;
    
    var SinergisChangePassword = AbstractAction.extend({
        template: "SinergisChangePassword",
    
        start: function () {
            var self = this;
            web_client.set_title('Changer le mot de passe');
            var $button = self.$('.oe_form_button');
            $button.appendTo(this.getParent().$footer);
            $button.eq(1).click(function () {
                self.$el.parents('.modal').modal('hide');
            });
            $button.eq(0).click(function () {
                self._rpc({
                        route: '/web/session/change_sinergis_password',
                        params: {
                            fields: $('form[name=sinergis_change_password_form]').serializeArray()
                        }
                    })
                    .then(function (result) {
                        if (result.error) {
                            self.displayNotification({
                                message: result.error,
                                type: 'danger'
                            });
                        } else {
                            self.do_action('logout');
                        }
                    });
            });
        },
    });
    
    core.action_registry.add("sinergis_change_password", SinergisChangePassword);
    
    return SinergisChangePassword;
    
    });
    