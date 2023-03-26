odoo.define('sinergis.all_companies', function(require) {
    "use strict";

    var utils = require('web.utils');

    $(document).ready(function() {
        if ($.bbq.getState('cids') != "1,2,3,5") {
            utils.set_cookie('cids', "1,2,3,5");
            $.bbq.pushState({'cids': "1,2,3,5"}, 0);
            location.reload();
        }
    });
        

});