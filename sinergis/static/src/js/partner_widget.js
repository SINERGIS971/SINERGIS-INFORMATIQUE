odoo.define('sinergis.UnlockTechnicalNotes', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var web_client = require('web.web_client');
    
    var _t = core._t;
    
    var SinergisUnlockTechnicalNotes = AbstractAction.extend({
        template: "UnlockTechnicalNotes",
    
        start: function () {
            var self = this;
            web_client.set_title('Débloquer les données techniques');
            var $button = self.$('.oe_form_button');
            $button.appendTo(this.getParent().$footer);
            $button.eq(1).click(function () {
                self.$el.parents('.modal').modal('hide');
            });
            $button.eq(0).click(function () {
                self._rpc({
                        route: '/web/session/unlock_technical_notes',
                        params: {
                            fields: {'pass': $('input[name=pass]').val()}
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
                                message: "Mot de passe correct",
                                type: 'success',
                            });
                            location.reload();
                        }
                    });
            });
        },
    });
    
    core.action_registry.add("sinergis_unlock_technical_notes", SinergisUnlockTechnicalNotes);
    
    return SinergisUnlockTechnicalNotes;
    
    });
    