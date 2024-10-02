odoo.define("sinergis.FormLeaveCheck", function (require) {
  "use strict";

  const FormController = require("web.FormController");
  const Dialog = require("web.Dialog");

  FormController.include({
    async canBeDiscarded(recordID) {
      // Appel du comportement par défaut d'Odoo
      const res = this._super.apply(this, arguments);

      // Récupération du modèle en cours
      const record = this.model.get(this.handle);

      // Vérification que le modèle est 'helpdesk.ticket'
      // Conditions :
      // - Mettre un message si nous quittons le modele avec une facturation CH mais pas de CH.
      // - Mettre un message si nous oublions de décompter le temps à facturer.
      if (record.model === "helpdesk.ticket") {
        const billing = record.data.x_sinergis_helpdesk_ticket_facturation;
        const contract = record.data.x_sinergis_helpdesk_ticket_tache2;
        if (billing == "Contrat heures" && !contract) {
          await Dialog.confirm(
            this,
            "Attention, vous avez séléctionner la facturation 'contrat d'heures' sans séléctionner de contrat !",
            {
              confirm_callback: () => {
                this._super.apply(this, arguments);
              },
            }
          );
          return false;
        } else if (billing == "Devis" || billing == "Contrat heures") {
            const time = record.data.x_sinergis_helpdesk_ticket_temps_passe;
            const is_billed = record.x_sinergis_helpdesk_ticket_is_facturee;
            if (time > 0 && !is_billed)
            {
                await Dialog.confirm(
                    this,
                    "Attention ! Vous allez quitter le ticket sans décompter vos heures sur la tâche !",
                    {
                      confirm_callback: () => {
                        this._super.apply(this, arguments);
                      },
                    }
                  );
                  return false;
            }
        }
      }

      return res;
    },
  });
});
