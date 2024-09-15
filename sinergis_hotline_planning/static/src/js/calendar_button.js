/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
patch(FormController.prototype, "sale_order", {
       setup(){
          this._super.apply();
          this.action = useService("action")
       },
       buttonClicked(){
           this.action.doAction({
               type: 'ir.actions.act_window',
               name: 'All Sale Orders',
               view_mode: 'form',
               views:[[false,"list"]],
               res_model: 'sale.order',
               target: 'new',
               context: "{'create' : False}",
           })
       }
});