# -*- coding: utf-8 -*-
{
    'name': 'ES: Core Modules',
    'category': 'Hidden',
    'version': '12.0.1',
    'author': 'Anniel Rodriguez Izquierdo',
    'summary': 'This module customize the odoo to work only with ERP STATION modules',
    'description': "",
    'depends': [
    ],
    'external_dependencies': {
        'python': [],
    },
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'data': [
        'views/ir_module_module.xml',
        'views/menu.xml',
    ],
    'auto_install': True,
    'pre_init_hook': '_es_core_module_pre_init_hook',
}
