# -*- coding: utf-8 -*-
import io
import os
import jinja2
import sys

import werkzeug
from datetime import datetime

from odoo.tools.misc import xlwt

from odoo import exceptions as odoo_exceptions, http, tools, service

from odoo.addons.web.controllers.main import DBNAME_PATTERN, db_monodb, Database as OdooDB

try:
    import json
except ImportError:
    import simplejson as json

from odoo import http, _, tools
from odoo.http import request, content_disposition
from ..scripts import builders, \
    pdf_builder as Pdf, \
    excel_builder as Excel

from .. import scripts

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.es_core', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

yap_app_name = tools.config.get('yap_app_name', None)
if not yap_app_name or yap_app_name is False or yap_app_name == '':
    yap_app_name = 'StarYaP'
    tools.config['yap_app_name'] = yap_app_name
    tools.config.save()


# ----------------------------------------------------------------------------------------------------------------------
# Controlador para el Widget de Alertas
# ----------------------------------------------------------------------------------------------------------------------
class NotificationController(http.Controller):

    @http.route('/notification/alert/load', type='json', auth='user')
    def load_alerts(self, req, **kwargs):
        alerts = []

        try:
            alerts = request.env['res.users'].systray_get_alerts()
        except:
            pass

        return {
            'counter': len(alerts),
            'alerts': alerts,
        }


# ----------------------------------------------------------------------------------------------------------------------
# Report Generator Controller
# ----------------------------------------------------------------------------------------------------------------------
class ReportGenerator(http.Controller):

    @http.route('/report/exporter', type='http', auth='user')
    def index(self, req, data, token):
        request_data = json.loads(data)
        # ------------------------------
        model = request_data.get('model', False)
        # ------------------------------
        view_id = request_data.get('view_id', False)
        no_leaf = request_data.get('no_leaf', False)
        group_by = request_data.get('group_by', '')

        domain = request_data.get('domain', [])
        domain = domain[0] if domain else []

        context = request_data.get('context', {})
        context.update(req.context)
        context.update({
            'view_id': view_id,
            'group_by': group_by,
            'group_by_no_leaf': no_leaf
        })
        sort = request_data.get('sort', req.env[model]._order)
        # ------------------------------
        pageCurrentMin = request_data.get('pageCurrentMin', 0)
        pageLimit = request_data.get('pageLimit', 80)
        # ------------------------------
        active_ids = request_data.get('active_ids', [])
        # ------------------------------
        report_title = request_data.get('report_title', 'No title')
        result_type = request_data.get('result_type', False)
        file_type = request_data.get('file_type', None)
        file_name = request_data.get('file_name', 'Non-Named')
        # ------------------------------
        ids = []
        if result_type == builders.KEY_SELECTED_ITEMS:
            ids = active_ids
        elif result_type == builders.KEY_VISIBLE_ITEMS:
            ids = req.env[model].search(domain, pageCurrentMin, pageLimit, order=','.join(sort or [])).ids
        elif result_type == builders.KEY_ALL_ITEMS:
            ids = req.env[model].search(domain, order=','.join(sort or [])).ids
        # ------------------------------
        if file_type == 'pdf':
            content_type = 'application/pdf'
            file_name += ".pdf"
            builder = Pdf.PDFBuilder()
        elif file_type == 'excel':
            content_type = 'application/vnd.ms-excel'
            file_name += ".xls"
            builder = Excel.ExcelBuilder()
        # ------------------------------
        report_params = {
            'title': report_title,
            'author': req.env.user.name,
            'company': req.env.user.company_id,
            'date': datetime.now().strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        }
        # ------------------------------
        result = builder.create(req, ids, model, domain, context, report_params)

        return http.send_file(io.BytesIO(result[0]), filename=file_name, as_attachment=True)


# ----------------------------------------------------------------------------------------------------------------------
# DataBase Generator Controller
# ----------------------------------------------------------------------------------------------------------------------
class Database(OdooDB):

    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = tools.config.verify_admin_password('admin')
        d['list_db'] = tools.config['list_db']
        d['langs'] = service.db.exp_list_lang()
        d['countries'] = service.db.exp_list_countries()
        d['pattern'] = DBNAME_PATTERN
        # databases list
        d['databases'] = []
        d['app_name'] = yap_app_name
        d['without_demo'] = tools.config['without_demo']
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = service.db.list_db_incompatible(d['databases'])
        except odoo_exceptions.AccessDenied:
            mono_db = db_monodb()
            if mono_db:
                d['databases'] = [mono_db]
        return env.get_template("yap_database_manager.html").render(d)
