/** @odoo-module **/
import SystrayMenu from "web.SystrayMenu";
import Widget from 'web.Widget';


var SinergisClaimsSystrayWidget = Widget.extend({
   template: 'SinergisClaimsSystray',
   events: {
       'click #sinergis_claims_so': '_onClick',
   },
   _onClick: function(){

       this.do_action({
            type: 'ir.actions.act_window',
            name: 'Réclamation',
            res_model: 'res.partner.claims',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
       });
   },
});

SystrayMenu.Items.push(SinergisClaimsSystrayWidget);
export default SinergisClaimsSystrayWidget;