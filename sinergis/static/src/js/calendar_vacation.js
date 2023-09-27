odoo.define('sinergis.CalendarView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var framework = require('web.framework');
    const CalendarRenderer = require('@calendar/js/calendar_renderer')[Symbol.for("default")].AttendeeCalendarRenderer;
    
    var _t = core._t;
    
    
    const CalendarVacationRenderer = CalendarRenderer.include({
    
        events: _.extend({}, CalendarRenderer.prototype.events, {
            'click .o_sinergis_add_vacation': '_addCalendarVacation',
        }),
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        _addCalendarVacation: function() {
            var action = {
                type: 'ir.actions.client',
                tag: 'sinergis_vacation_builder',
                target: 'new',
            };
            this.do_action(action);
        },

    });
    
    return {
        CalendarVacationRenderer,
    };
    
    });
    