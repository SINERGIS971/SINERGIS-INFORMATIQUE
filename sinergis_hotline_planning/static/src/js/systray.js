/** @odoo-module **/
import SystrayMenu from "web.SystrayMenu";
import Widget from 'web.Widget';


var HotlinePlanningSystrayWidget = Widget.extend({
   template: 'HotlinePlanningSystray',
   events: {
       'click #planning_hotline_so': '_onClick',
   },
   _onClick: function(){

    const date = new Date();
    let day = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();
    let currentDate = `${year}-${month}-${day}`;

       this.do_action({
            type: 'ir.actions.act_window',
            name: 'Hotline',
            res_model: 'sinergis_hotline_planning.event',
            view_mode: 'list',
            views: [[false, 'list']],
            domain: [['date','=', currentDate]],
            target: 'new',
            context: {'create':false,'edit':false}
       });
   },
});

SystrayMenu.Items.push(HotlinePlanningSystrayWidget);
export default HotlinePlanningSystrayWidget;