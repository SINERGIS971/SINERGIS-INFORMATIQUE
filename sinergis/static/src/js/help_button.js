odoo.define('sinergis.help_button', function(require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');

    var _t = core._t;

    $(document).ready(function() {
        $('.reste_password_limit_button').click(function() {
            rpc.query({
                model: 'my.model',
                method: 'my_function',
                args: [],
            }).then(function(result) {
                // Do something with the result
            });
        });
    });
});