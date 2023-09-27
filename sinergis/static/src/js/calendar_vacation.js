odoo.define('sinergis.CalendarView', function (require) {
    "use strict";
    
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var framework = require('web.framework');
    const CalendarView = require('@calendar/js/calendar_view')[Symbol.for("default")];
    const CalendarRenderer = require('@calendar/js/calendar_renderer')[Symbol.for("default")].AttendeeCalendarRenderer;
    const CalendarController = require('@calendar/js/calendar_controller')[Symbol.for("default")];
    const CalendarModel = require('@calendar/js/calendar_model')[Symbol.for("default")];
    const viewRegistry = require('web.view_registry');
    const session = require('web.session');
    
    var _t = core._t;
    
    
    const CalendarVacationRenderer = CalendarRenderer.include({
    
        events: _.extend({}, CalendarRenderer.prototype.events, {
            'click .o_sinergis_add_vacation': '_addCalendarVacation',
        }),
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        _addCalendarVacation: function() {
            console.log("Hello world");
        },

    });
    
    return {
        CalendarVacationRenderer,
    };
    
    });
    