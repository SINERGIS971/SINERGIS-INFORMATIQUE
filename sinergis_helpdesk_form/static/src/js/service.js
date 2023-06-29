/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";


export const sensitiveFileMenuService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {

        return {
            display_sensitive_file_menu() {
                const last_update_date = env.services.orm.call("sinergis_rgpd.sensitive_data", "is_sensitive_data_to_remove")
                last_update_date.then((result) => {
                  const stringResult = JSON.stringify(result).replaceAll('"', '');
                  //console.log(stringResult);
                  const elements = document.querySelectorAll('.sinergis_rgpd_sensitive_file_menu');
                  if (stringResult == "false") {
                      elements.forEach(element => element.remove());
                  } else {
                      elements.forEach(element => {element.style.visibility="visible"; element.style.width="auto"});
                  }
                }).catch((error) => {
                  console.error(error);
                });
            },
            async load_page() {
                const actionDescription = await env.services.orm.call("sinergis_rgpd.sensitive_data", "display_tree_view")
                actionDescription.res_id = env.services.user.userId
                env.services.action.doAction(actionDescription);
            }
        };
    },
};

registry.category("services").add("sensitive_file_menu_service", sensitiveFileMenuService);
