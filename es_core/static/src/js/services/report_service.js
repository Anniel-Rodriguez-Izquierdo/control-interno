odoo.define('es_core.service.ReportService', function (require) {
"use strict";

var AbstractService = require('web.AbstractService');
var Bus = require('web.Bus');
var config = require('web.config');
var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var Dialog = require('web.Dialog');
var QWeb = core.qweb;
var crash_manager = require('web.crash_manager');

var _t = core._t;

var ReportService =  AbstractService.extend({
    dependencies: ['ajax', 'bus_service'],

    start: function () {
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    open_modal_form: function (current_view) {
        var self = this;

        var search_filters = current_view.searchView.fields_view.arch.children;
        var filters = [];
        _.each(search_filters, function (filter) {
            //if (item.tag === 'filter') {
            filters.push(filter);
            //}
        });

        self.EXPORT_DIALOG = new Dialog(this, {
            backdrop: true,
            size: 'medium',
            title: _t("Export: ") + current_view.displayName,
            $content: QWeb.render('ExportView', {
                file_name: current_view.displayName
            }),
            buttons: [
                {
                    text: _t("Export"),
                    click: function () {
                        self.export(current_view);
                    }
                }, {
                    text: _t("Close"),
                    click: function () {
                        self.EXPORT_DIALOG.close();
                    }
                }
            ]
        });
        self.EXPORT_DIALOG.open();
    },

    export: function (current_view) {
        var self = this;
        //----------------------------------
        var viewID = false
        var viewType = current_view.viewType;
        _.each(current_view.actionViews, function(view){
            if(view.type == viewType)
                viewID = view.viewID;
        });
        var search_data = current_view.searchView.build_search_data()
        //----------------------------------
        var _model = current_view.modelName;
        //----------------------------------
        var _view_id = viewID;
        var _no_leaf = current_view.noLeaf ;
        var _domain = search_data.domains;
        var _context = search_data.context;
        var _group_by = search_data.groupbys;
        var _sort = false;
        //----------------------------------
        var _active_ids = current_view.getSelectedIds();
        //----------------------------------
        var _pageCurrentMin = current_view.pager.state.current_min;
        var _pageLimit = current_view.pager.state.limit;
        //----------------------------------
        var _report_title = current_view.displayName;
        var _result_type = self.EXPORT_DIALOG.$el.find('[name="result_type"]:checked').val();
        var _file_type = self.EXPORT_DIALOG.$el.find('[name="file_type"]:checked').val();
        var _file_name = self.EXPORT_DIALOG.$el.find('#file_name').val();
        //----------------------------------
        framework.blockUI();
        session.get_file({
            url: '/report/exporter',
            data: {
                data: JSON.stringify({
                    view_id: _view_id,
                    model: _model,
                    domain: _domain,
                    context: _context,
                    group_by: _group_by,
                    no_leaf: _no_leaf,
                    sort: _sort,
                    pageCurrentMin: _pageCurrentMin,
                    pageLimit: _pageLimit,
                    active_ids: _active_ids,
                    report_title: _report_title,
                    result_type: _result_type,
                    file_type: _file_type,
                    file_name: _file_name
                })
            },
            complete: function (opts) {
                framework.unblockUI();
                self.EXPORT_DIALOG.close();
            },
            error: crash_manager.rpc_error.bind(crash_manager),
        });
    },
});

core.serviceRegistry.add('report_service', ReportService);

return ReportService;

});
