/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { session } from "@web/session";

export function changePassword(env) {
    return {
        type: "item",
        id: "change_password",
        description: env._t("Change Password"),
        callback: async function () {
            const actionDescription = await env.services.orm.call("res.users", "sinergis_action_get");
            actionDescription.res_id = env.services.user.userId;
            env.services.action.doAction(actionDescription);
        },
        sequence: 50,
    };
}

registry
    .category("user_menuitems")
    .add("change_password", changePassword)