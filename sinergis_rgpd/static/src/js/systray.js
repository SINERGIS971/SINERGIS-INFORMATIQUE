/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

const { Component, hooks } = owl;
const { useState } = hooks;



export class SinergisSensitiveFileMenu extends Component {
    setup() {
        this.companyService = useService("sensitive_file_menu_service");
        this.companyService.display_sensitive_file_menu();
    }
    
    openSensitiveFileList(companyId) {
       this.companyService.load_page();
    }
}
SinergisSensitiveFileMenu.template = "sinergis_rgpd.SinergisSensitiveFileMenu";
SinergisSensitiveFileMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SinergisSensitiveFileMenu,
    isDisplayed(env) {
        return true;
    },
};

registry.category("systray").add("SinergisSensitiveFileMenu", systrayItem, { sequence: 3 });
