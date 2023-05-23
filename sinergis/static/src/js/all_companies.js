odoo.define('sinergis.all_companies', function(require) {
    "use strict";

    var utils = require('web.utils');
    var session = require('web.session');

    $(document).ready(function() {
        
        var refresh = false;
        const state = $.bbq.getState('cids');
        var cids_array = [];
        const allowedCompanies = session.user_companies.allowed_companies;
        
        for (var allowedCompany in allowedCompanies) {
            cids_array.push(allowedCompany.toString());
            if (!state.includes(allowedCompany.toString())) {
                refresh = true;
            }  
        }
        
        if (refresh) {
            const cids = cids_array.join(',');
            utils.set_cookie('cids', cids);
            $.bbq.pushState({'cids': cids}, 0);
            location.reload();
        }
        
    });
        

});