/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";


function isDateMoreThan90DaysAgo(dateString) {
  const date = new Date(dateString);
  const timeDiff = Date.now() - date.getTime();
  const daysDiff = timeDiff / (1000 * 3600 * 24);
  return daysDiff >= 90;
}

export const changePasswordService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {

        return {
            display_change_password_menu() {
                const last_update_date = env.services.orm.call("res.users", "sinergis_get_last_update")
                last_update_date.then((result) => {
                  const stringResult = JSON.stringify(result).replaceAll('"', '');
                  console.log(stringResult);
                  if (stringResult != "false" && !isDateMoreThan90DaysAgo(stringResult)) {
                      const elements = document.querySelectorAll('.sinergis_change_password_menu');
                      elements.forEach(element => element.remove());
                  }
                }).catch((error) => {
                  console.error(error);
                });
            },
            async load_page() {
                const actionDescription = await env.services.orm.call("res.users", "sinergis_action_get")
                actionDescription.res_id = env.services.user.userId
                env.services.action.doAction(actionDescription);
            }
        };
    },
};

registry.category("services").add("change_password", changePasswordService);
