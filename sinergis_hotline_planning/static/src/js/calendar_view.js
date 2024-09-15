/** @odoo-module alias=calendar.CalendarView **/

import CalendarController from '@sinergis_hotline_planning/js/calendar_controller';
import CalendarModel from '@sinergis_hotline_planning/js/calendar_model';
import AttendeeCalendarRenderer from '@sinergis_hotline_planning/js/calendar_renderer';
import CalendarView from 'web.CalendarView';
import viewRegistry from 'web.view_registry';

const CalendarRenderer = AttendeeCalendarRenderer.AttendeeCalendarRenderer;

var HotlineCalendarView = CalendarView.extend({
    config: _.extend({}, CalendarView.prototype.config, {
        Renderer: CalendarRenderer,
        Controller: CalendarController,
        Model: CalendarModel,
    }),
});

viewRegistry.add('hotline_calendar', HotlineCalendarView);

export default HotlineCalendarView;
