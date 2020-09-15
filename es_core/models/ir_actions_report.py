# -*- coding: utf-8 -*-
# Copyright 2020 StarYAP
#   PaKaMa <pablocm83@gmail.com>
#   Develop by StarYaP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, api


class SYAPIrActionReport (models.Model):
    _inherit = 'ir.actions.report'
    _description = 'Report Action'

    @api.model
    def _build_wkhtmltopdf_args(
            self,
            paperformat_id,
            landscape,
            specific_paperformat_args=None,
            set_viewport_size=False):
        res = super(SYAPIrActionReport, self)._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args,
            set_viewport_size)

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-bottom'):
            res.extend(['--margin-bottom', str(specific_paperformat_args['data-report-margin-bottom'])])
        else:
            res.extend(['--margin-bottom', str(paperformat_id.margin_bottom)])
        return res
