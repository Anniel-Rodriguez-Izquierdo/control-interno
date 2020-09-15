# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def _es_core_module_pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    module_list = ['es_core']
    modules = env['ir.module.module'].search([('name', 'in', module_list), ('state', '=', 'uninstalled')])
    modules.sudo().button_install()
