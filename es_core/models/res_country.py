# -*- coding: utf-8 -*-

from odoo import models, fields
from .. import scripts


class ResCountry(models.Model):
    _inherit = 'res.country'

    street_format = fields.Text(compute=lambda self: scripts.CUBAN_FORMAT_ADDRESS)


class ResCountryStateCity(models.Model):
    _name = 'res.country.state.city'
    _description = 'no description'

    name = fields.Char(string='Name', required=True)
    code = fields.Char('City code',
                       size=5,
                       required=True)
    state_id = fields.Many2one("res.country.state", string='State', required=True)

    zip = fields.Char('ZIP',
                      required=False)
    other_zip = fields.Char('ZIP 2',
                            required=False)
    country_id = fields.Many2one('res.country',
                                 related='state_id.country_id',
                                 string='Country',
                                 readonly=True,
                                 store=False)
