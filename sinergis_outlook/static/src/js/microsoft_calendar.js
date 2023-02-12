odoo.define('sinergis_outlook.CalendarView', function (require) {
    "use strict";

const CalendarRenderer = require('@calendar/js/calendar_renderer')[Symbol.for("default")].AttendeeCalendarRenderer;
const CalendarController = require('@calendar/js/calendar_controller')[Symbol.for("default")];

const SinergisOutlookCalendarRenderer = CalendarRenderer.include({
    events: _.extend({}, CalendarRenderer.prototype.events, {
        'click .o_sinergis_outlook_sync_pending': '_onSyncMicrosoftCalendar',
    }),

    _onSyncMicrosoftCalendar: function () {
        var self = this;
        this.$microsoftButton.prop('disabled', true);
        this.trigger_up('syncMicrosoftCalendar', {
            on_always: function () {
                self.$microsoftButton.prop('disabled', false);
            },
            /*on_refresh: function () {
                self._initMicrosoftPillButton();
            }*/
        });
    },

});

//Microsoft Controller
const SinergisOutlookCalendarController = CalendarController.include({
    custom_events: _.extend({}, CalendarController.prototype.custom_events, {
        syncMicrosoftCalendar: '_onSyncMicrosoftCalendar',
    }),
    _onSyncMicrosoftCalendar: function (event) {
        var self = this;
        Dialog.alert(self, _t("You will be redirected to Outlook to authorize the access to your calendar."), {
            confirm_callback: function() {
                // URL
                
                //framework.redirect(o.url);
            },
            title: _t('Redirection'),
        });
    },


});

});