# -*- coding: utf-8 -*-
from odoo import fields, models


# para permitir que en la vista puedan definir un nuevo tipo: DASHBOARD
class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('dashboard', "Dashboard")])
