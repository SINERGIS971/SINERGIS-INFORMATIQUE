/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { session } from "@web/session";

export function openSensitiveFileList(env) {
    return {
        type: "item",
        id: "open_sensitive_file_list",
        description: env._t("Ouvrir la liste des dossiers sensibles"),
        callback: async function () {
            //const actionDescription = await env.services.orm.call("res.users", "sinergis_action_get");
            //actionDescription.res_id = env.services.user.userId;
            env.services.action.doAction({
                name: "Données sensibles",
                res_model: "sinergis_rgpd.sensitive_data",
                views: [[false, "tree"],[false, "form"]],
                type: "ir.actions.act_window",
                view_mode: "tree",
                target: "new",
            });
        },
        sequence: 50,
    };
}

registry
    .category("user_menuitems")
    .add("open_sensitive_file_list", openSensitiveFileList)