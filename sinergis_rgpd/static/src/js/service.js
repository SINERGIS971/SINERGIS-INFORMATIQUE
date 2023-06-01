/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";


export const sensitiveFileMenuService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {

        return {
            display_change_password_menu() {
            },
            async load_page() {
                const actionDescription = await env.services.orm.call("res.users", "sinergis_action_get")
                actionDescription.res_id = env.services.user.userId
                env.services.action.doAction(actionDescription);
            }
        };
    },
};

registry.category("services").add("sensitive_file_menu_service", sensitiveFileMenuService);
