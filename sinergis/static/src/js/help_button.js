odoo.define('sinergis.help_button', function(require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var _t = core._t;

    $(document).ready(function() {
        $('.reset_password_limit_button').click(function() {
            new view_dialogs.FormViewDialog(this, {
                res_model: 'res.users',
                res_id: session.uid,
                title: "Utilisateur",
                on_saved: function (record) {
                    console.log("Click Save");
                }
             }).open();
        });
    });
});