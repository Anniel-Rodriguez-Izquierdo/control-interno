# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID, _
from . import tools
from . import scripts
from . import models, controllers, validation
from . import wizards
from odoo.exceptions import ValidationError


def _es_core_pre_init_hook(cr):
    with cr.savepoint():
        users = []
        cr.execute("SELECT login FROM res_users")
        for user in cr.fetchall():
            login = user[0].lower()
            if login not in users:
                users.append(login)
            else:
                raise ValidationError(
                    _('Conflicting user login exist for `%s`' % login)
                )


def _es_core_post_init_hook(cr, registry):
    with cr.savepoint():
        env = api.Environment(cr, SUPERUSER_ID, {})

        env.ref('base.group_no_one')._check_no_one_group()

        cr.execute("UPDATE res_users SET login=lower(login)")
        modules_to_install = ['']
        modules = env['ir.module.module'].search([('name', 'in', modules_to_install), ('state', '=', 'uninstalled')])
        modules.sudo().button_install()
