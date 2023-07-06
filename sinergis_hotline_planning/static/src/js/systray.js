/** @odoo-module **/
import SystrayMenu from "web.SystrayMenu";
import Widget from 'web.Widget';

import { session } from "@web/session";

var HotlinePlanningSystrayWidget = Widget.extend({
   template: 'HotlinePlanningSystray',
   events: {
       'click #create_so': '_onClick',
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
            view_mode: 'tree',
            views: [[false, 'tree']],
            domain: [['date','=', currentDate]],
            target: 'new'
       });
   },
});

SystrayMenu.Items.push(HotlinePlanningSystrayWidget);
export default HotlinePlanningSystrayWidget;