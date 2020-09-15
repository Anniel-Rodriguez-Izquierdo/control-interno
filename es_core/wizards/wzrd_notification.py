# -*- coding: utf-8 -*-

from odoo import api, models, fields


class WzrdNotification(models.TransientModel):
    _name = 'wzrd.notification'
    _description = 'no description'

    message = fields.Html('Message', require=True, readonly=True)
    message_type = fields.Selection(selection=[('success', 'Success')], string='Type', require=True)
    next_action = fields.Char('Next Action', readonly=True)

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------
    @api.multi
    def action_close(self):
        if self.next_action:
            action = self.env.ref(self.next_action).read()[0]
            action['target'] = 'main'
            return action
