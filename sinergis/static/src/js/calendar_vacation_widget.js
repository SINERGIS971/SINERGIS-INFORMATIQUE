odoo.define('sinergis.CalendarVacation', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var web_client = require('web.web_client');
    
    var _t = core._t;
    
    var SinergisVacationBuilder = AbstractAction.extend({
        template: "SinergisVacationBuilder",
    
        start: function () {
            var self = this;
            web_client.set_title('Poser des congés');
            var $button = self.$('.oe_form_button');
            $button.appendTo(this.getParent().$footer);
            $button.eq(1).click(function () {
                self.$el.parents('.modal').modal('hide');
            });
            $button.eq(0).click(function () {
                self._rpc({
                        route: '/web/session/change_sinergis_password',
                        params: {
                            fields: $('form[name=sinergis_vacation_builder_form]').serializeArray()
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
    
    core.action_registry.add("sinergis_vacation_builder", SinergisVacationBuilder);
    
    return SinergisVacationBuilder;
    
    });
    