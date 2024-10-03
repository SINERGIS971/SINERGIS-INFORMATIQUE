odoo.define('sinergis.FormLeaveCheck', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const Dialog = require('web.Dialog');

    FormController.include({

        // Méthode appelée lorsque la vue va être changée
        on_detach_callback: function () {
            const record = this.model.get(this.handle);

            // Vérifier si le modèle est 'helpdesk.ticket'
            if (record && record.model === 'helpdesk.ticket') {
                const fieldValue = record.data.x_field_name; // Remplacer par le nom de votre champ

                // Si le champ est vide, afficher la confirmation avant de quitter
                if (!fieldValue) {
                    const confirmation = confirm('Ce champ n\'est pas rempli. Êtes-vous sûr de vouloir quitter cette page ?');
                    if (!confirmation) {
                        // Bloquer la navigation
                        return false;
                    }
                }
            }

            // Appeler le comportement par défaut d'Odoo (permettre la navigation)
            return this._super.apply(this, arguments);
        },
    });

});
