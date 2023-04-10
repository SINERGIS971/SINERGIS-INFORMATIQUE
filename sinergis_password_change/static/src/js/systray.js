/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

const { Component, hooks } = owl;
const { useState } = hooks;



export class ChangePasswordMenu extends Component {
    setup() {
        this.companyService = useService("change_password");
        this.companyService.display_change_password_menu();
    }
    
    changePassword(companyId) {
        this.companyService.load_page();
    }
}
ChangePasswordMenu.template = "sinergis_password_change.SinergisChangePasswordMenu";
ChangePasswordMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: ChangePasswordMenu,
    isDisplayed(env) {
        return true;
    },
};

registry.category("systray").add("ChangePasswordMenu", systrayItem, { sequence: 2 });
