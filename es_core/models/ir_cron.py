# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class IrCron(models.Model):
    _inherit = 'ir.cron'

    action_result_text = fields.Text('Action Value Returned', help='Use internal only')
    action_result_numeric = fields.Float('Action Value Returned', help='Use internal only')
    action_result_boolean = fields.Boolean('Action Value Returned', help='Use internal only')

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.multi
    def method_direct_trigger(self):
        self.check_access_rights('write')

        for cron in self:
            value_returned = self.sudo(user=cron.user_id.id).ir_actions_server_id.run()

            if isinstance(value_returned, dict) and len(value_returned) == 3:
                cron.action_result_text = value_returned['result_text']
                cron.action_result_numeric = value_returned['result_numeric']
                cron.action_result_boolean = value_returned['result_boolean']

        return True
