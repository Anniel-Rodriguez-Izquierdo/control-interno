odoo.define('es_core.systray.AlertMenu', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Notification = require('web.Notification');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var pyUtils = require('web.py_utils');

    var ALERT_COUNTER_KEY = 'es_core.alert_counter';

    var AlertMenu = Widget.extend({
        name: 'alert_menu',
        template:'es_core.systray.AlertMenu',
        events: {
            'click .o_alert_preview': '_onAlertClick',
        },
        start: function () {
            this._super.apply(this, arguments);

            this._$alertPreview = this.$('.o_alert_systray_dropdown_items');
            this._$notificationCounter = this.$('.o_notification_counter');

            this.call('local_storage', 'setItem', ALERT_COUNTER_KEY, 0);

            core.bus.on('on_load_alert', this, this._renderAlerts);

            this.call('alert_service', 'loadAlertsFromServer');
        },

        //------------------------------------------------------------
        // Private
        //------------------------------------------------------------
        _renderAlerts: function(result){
            this._updateCounter(result);
            this._updateNotification(result);
            this._updateAlertPreview(result);
        },

        _updateCounter: function(result){
            var counter = result.counter;

            this.$el.toggleClass('o_no_notification', !counter);

             if(counter > 0) {
                if(!this.$el.find('i.fa-bell').hasClass('bell_effect'))
                    this.$el.find('i.fa-bell').addClass('bell_effect');
             } else {
                this.$el.find('i.fa-bell').removeClass('bell_effect');
             }

            if(counter >= 100) {
                counter = '+99'
            }

            this._$notificationCounter.text(counter);
        },

        _updateNotification: function(result){
            var stored_counter = this.call('local_storage', 'getItem', ALERT_COUNTER_KEY);

            if(result.counter > stored_counter)
                this.call('sound_service', 'play_alert_beep');

            this.call('local_storage', 'setItem', ALERT_COUNTER_KEY, result.counter);
        },

        _updateAlertPreview: function(result){
            this._$alertPreview.html(QWeb.render('es_core.systray.AlertMenu.Previews', {
                counter : result.counter,
                alerts : result.alerts
            }));
        },

        _onAlertClick: function (event) {
            // fetch the data from the button otherwise fetch the ones from the parent (.o_alert_preview).
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
            var context = {};

            if(data.action !== undefined && data.action !== false) {
                this.do_action(data.action);
            } else {
                if (data.res_model !== undefined && data.res_model !== false) {
                    this.do_action({
                        type: 'ir.actions.act_window',
                        name: data.title,
                        res_model:  data.res_model,
                        views: [[false, 'list'], [false, 'form']],
                        view_type: 'list',
                        view_mode: 'form',
                        search_view_id: [false],
                        domain: data.domain,
                        context:context,
                        target:'main',
                    });
                }
            }
        },
    });

    SystrayMenu.Items.push(AlertMenu);

    return AlertMenu;
});