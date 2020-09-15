# -*- coding: utf-8 -*-

from odoo import api, models, fields


class Groups(models.Model):
    _inherit = 'res.groups'

    active = fields.Boolean(string='Active', default=True)

    # -------------------------------------------------------------------------
    # ORM SECTION
    # -------------------------------------------------------------------------
    @api.model_cr
    def _register_hook(self):
        self.search([])._check_no_one_group()

    @api.multi
    @api.constrains('rule_groups', 'menu_access', 'view_access')
    def _check_no_one_group(self):
        # el objetivo es eliminarle al grupo todas las referencias a los elementos a los que se le aplicó

        group_no_one_id = self.env.ref('base.group_no_one').id

        self._cr.execute("""DELETE FROM %s WHERE %s = %s""" % (self._fields['rule_groups'].relation,
                                                               self._fields['rule_groups'].column1,
                                                               group_no_one_id))

        self._cr.execute("""DELETE FROM %s WHERE %s = %s""" % (self._fields['menu_access'].relation,
                                                               self._fields['menu_access'].column1,
                                                               group_no_one_id))

        self._cr.execute("""DELETE FROM %s WHERE %s = %s""" % (self._fields['view_access'].relation,
                                                               self._fields['view_access'].column1,
                                                               group_no_one_id))
