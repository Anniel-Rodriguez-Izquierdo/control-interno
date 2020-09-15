odoo.define('es_core.service.AlertService', function (require) {
"use strict";

    var AbstractService = require('web.AbstractService');
    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');

    var AlertService =  AbstractService.extend({
        dependencies: ['ajax', 'bus_service'],

        start: function () {
            this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
        loadAlertsFromServer: function() {
            var self = this;

            var context = _.extend(
                { isMobile: config.device.isMobile },
                session.user_context
            );

            session.rpc('/notification/alert/load', context, { shadow: true }).then(function (result) {
                core.bus.trigger('on_load_alert', result);

                //load alerts every 15 sec
                setTimeout(function(){
                    self.loadAlertsFromServer();
                }, 15000);
            });
        }
    });

    core.serviceRegistry.add('alert_service', AlertService);

    return AlertService;
});