odoo.define('sinergis.FormLeaveCheck', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const Dialog = require('web.Dialog');

    FormController.include({
        async canBeDiscarded(recordID) {
            // Appel du comportement par défaut d'Odoo
            const res = this._super.apply(this, arguments);

            // Récupération du modèle en cours
            const record = this.model.get(this.handle);

            // Vérification que le modèle est 'helpdesk.ticket'
            if (record.model === 'helpdesk.ticket') {
                // Vérification d'un champ spécifique (par exemple, x_field_name)
                //const fieldValue = record.data.x_field_name;

                // Si le champ n'est pas rempli (vide ou null), afficher une confirmation avant de quitter
                if (true) {
                    await Dialog.confirm(this, 'Ce champ n\'est pas rempli. Êtes-vous sûr de vouloir quitter ?', {
                        confirm_callback: () => {
                            // Si l'utilisateur confirme, on autorise à quitter la vue
                            this._super.apply(this, arguments);
                        },
                    });
                    // Retourne `false` pour empêcher la fermeture du formulaire immédiatement
                    return false;
                }
            }

            // Si ce n'est pas le modèle helpdesk.ticket, ou si le champ est rempli, on continue normalement
            return res;
        },
    });
});
