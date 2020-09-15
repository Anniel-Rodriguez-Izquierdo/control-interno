# -*- coding: utf-8 -*-
import os
import sys

try:
    import json
except ImportError:
    import simplejson as json

import jinja2

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.es_core', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

from odoo.http import request
from odoo import http


# ----------------------------------------------------------------------------------------------------------------------
# Controlador para gestionar el formulario para resolver la guia de control
# ----------------------------------------------------------------------------------------------------------------------
class AutoControlGuideController(http.Controller):

    @http.route('/ic/open_guide/<int:gui_id>', type='http', auth="public", website=True)
    def open_guide(self, gui_id, **kwargs):
        components = {}
        for question in request.env['syap.ic.guide'].browse(gui_id).question_ids:
            # registro el componente-------------------
            components.setdefault(question.component_id.code, {
                'title': question.component_id.name,
                'topics': {},
            })
            # registro el topico-----------------------
            components[question.component_id.code]['topics'].setdefault(question.topic_id.code, {
                'title': question.topic_id.name,
                'questions': [],
            })
            # registro la pregunta---------------------
            components[question.component_id.code]['topics'][question.topic_id.code]['questions'].append(question)

        template_xml_id = 'syap_control_interno.autocontrol_guide_template'
        template_data = {
            'components': components
        }
        ActionReport = request.env['ir.actions.report']
        body = ActionReport.render_template(template_xml_id, values=template_data)
        body = body.decode('utf-8')

        return body
