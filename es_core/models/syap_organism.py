# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models, fields, _
from .. import scripts


class SYAPOrganism(models.Model):
    _name = 'syap.organism'
    _description = 'Organism'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    short = fields.Char('Short', required=True)
    active = fields.Boolean('Active?', default=True)

    _sql_constraints = [
        ('code_unique',
         'UNIQUE (code)',
         _("Organism's code must be unique!"))]
