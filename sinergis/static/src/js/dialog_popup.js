odoo.define('sinergis.dialog_popup', function (require) {
    "use strict";
    
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var CustomDialog = Widget.extend({
        events: {
            'click .btn-popover': 'on_button_click',
        },
        start: function() {
            var self = this;
            var options = {
                title: "Titre de la fenêtre dialog",
                size: 'medium',
                buttons: [{
                    text: "Fermer",
                    classes: 'btn-primary',
                    close: true,
                }],
                //$content: QWeb.render('nom_de_votre_template'),
            };
            this.dialog = new Dialog(this, options).open();
            return this._super.apply(this, arguments);
        },
        on_button_click: function() {
            this.dialog.close();
        },
    });

    return CustomDialog;
    });
    