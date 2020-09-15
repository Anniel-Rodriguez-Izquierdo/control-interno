{
    'name': 'ES: Core',
    'category': 'Hidden',
    'version': '12.0.1',
    'author': 'Anniel Rodriguez Izquierdo',
    'summary': 'This module is the core of the ERP STATION Solutions.',
    'depends': [
        # ODOO modules
        'base',
        'web',
        'utm',
        'web_tour',
        'base_setup',
        'mail',
        'fetchmail',
        'web_settings_dashboard',
    ],
    'external_dependencies': {
        'python': ['passlib'],
    },
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # data
        'data/res.currency.csv',
        'data/yap_res_company_data.xml',
        'data/connection_data.xml',
        'data/parameter_data.xml',
        'data/yap_res_country_group_data.xml',
        'data/yap_res_country_data.xml',
        'data/res.country.state.csv',
        'data/res.country.state.city.csv',
        'data/crons.xml',
        # views
        'views/assets.xml',
        'views/menu.xml',
        'views/res_partner_views.xml',
        'views/res_company_view.xml',
        'views/res_country_view.xml',
        'views/res_users.xml',
        'views/res_groups.xml',
        'views/report_detail.xml',
        # external providers
        'views/datasource_providers.xml',
        # wizards
        'wizards/wzrd_notification_views.xml',
    ],
    'auto_install': True,
    'bootstrap': True,
    'pre_init_hook': '_es_core_pre_init_hook',
    'post_init_hook': '_es_core_post_init_hook',
}
