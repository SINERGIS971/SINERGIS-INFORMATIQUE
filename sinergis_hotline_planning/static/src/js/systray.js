import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';
var ExampleWidget = Widget.extend({
   template: 'SaleOrderSystray',
   events: {
       'click #create_so': '_onClick',
   },
   _onClick: function(){
       this.do_action({
            type: 'ir.actions.act_window',
            name: 'Sale Order',
            res_model: 'sale.order',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new'
       });
   },
});
SystrayMenu.Items.push(ExampleWidget);
export default ExampleWidget;