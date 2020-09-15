# -*- coding: utf-8 -*-
{
    'name': 'StarYAP: Control Interno',
    'category': 'Control Interno',
    'version': '12.0.1',
    'author': 'Anniel Rodriguez Izquierdo',
    'summary': "",
    'description': "",
    'depends': [
        'es_core',
    ],
    'external_dependencies': {
        'python': [],
    },
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/aoi_data.xml',
        'views/structures_views.xml',
        'views/guide_views.xml',
        'views/guide_question_views.xml',
        'views/component_views.xml',
        'views/area_of_interest_views.xml',
        'views/topics_views.xml',
        'views/question_explanation_views.xml',
        'views/menu.xml',
    ],
    'application': True
}
