odoo.define('es_core.view.export', function (require) {
"use strict";

    var config = require('web.config');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    /************************************************
    *    Mixins that enable the 'Export' feature    *
    ************************************************/
    var ExportViewMixin = {
        /**
         * @override
         * @param {Object} params
         * @param {boolean} [params.export_enabled=true] determine if the export
         *   button is visible (in the control panel)
         */
        init: function (viewInfo, params) {
            var exportEnabled = 'export_enabled' in params ? params.export_enabled : false;
            this.controllerParams.exportEnabled = exportEnabled && !config.device.isMobile;
        },
    };

    var ExportControllerMixin = {
        /**
         * @override
         */
        init: function (parent, model, renderer, params) {
            this.exportEnabled = params.exportEnabled;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * Adds an event listener on the export button.
         *
         * @private
         */
        bindExport: function () {
            if (!this.$buttons) {
                return;
            }
            var self = this;
            this.$buttons.on('click', '.o_button_export', function () {
                self.call('report_service', 'open_modal_form', self)
            });
        }
    };

    /************************************************
    *    Activate 'Export' feature on List views    *
    ************************************************/
    ListView.include({
        init: function () {
            this._super.apply(this, arguments);
            ExportViewMixin.init.apply(this, arguments);
        },
    });

    ListController.include({
        init: function () {
            this._super.apply(this, arguments);
            ExportControllerMixin.init.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Extends the renderButtons function of ListView by adding an event listener
         * on the import button.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments); // Sets this.$buttons
            ExportControllerMixin.bindExport.call(this);
        }
    });

    /************************************************
    *    Activate 'Export' feature on Kanban views  *
    ************************************************/
    KanbanView.include({
        init: function () {
            this._super.apply(this, arguments);
            ExportViewMixin.init.apply(this, arguments);
        },
    });

    KanbanController.include({
        init: function () {
            this._super.apply(this, arguments);
            ExportControllerMixin.init.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Extends the renderButtons function of ListView by adding an event listener
         * on the import button.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments); // Sets this.$buttons
            ExportControllerMixin.bindExport.call(this);
        }
    });
});