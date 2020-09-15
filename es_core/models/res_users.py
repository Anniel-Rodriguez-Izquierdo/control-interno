# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from .. import scripts


class Users(models.Model):
    _inherit = 'res.users'

    login = fields.Char(required=True,
                        help="Used to log into the system")

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['login'] = values.get('login', '').lower()
        return super(Users, self.with_context(default_customer=False)).create(vals_list)

    @api.multi
    def write(self, values):
        if values.get('login'):
            values['login'] = values['login'].lower()
        return super(Users, self).write(values)

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        login = login.lower()
        return super(Users, cls).authenticate(db, login, password, user_agent_env)

    # -------------------------------------------------------------------------
    # COMPUTE SECTION
    # -------------------------------------------------------------------------
    @api.model
    def systray_get_alerts(self):
        alerts = []

        # ---------------------------------------------
        # Reminder: users without emails
        # ---------------------------------------------
        if self.mixin_check_groups(['base.group_system']):
            new_alert = self.mixin_create_alert(res_model='res.users',
                                                domain=[('email', '=', False)],
                                                title=scripts.USER_ALERT_TITLE,
                                                message=scripts.USER_WITHOUT_EMAIL_ALERT_MESSAGE)
            if new_alert:
                alerts.append(new_alert)

            # ---------------------------------------------
            # Reminder: sql helper without provider
            # ---------------------------------------------
            new_alert = self.mixin_create_alert(res_model='es.sql.helper',
                                                domain=[('provider_ids', '=', False)],
                                                title=scripts.EXTERNAL_CONNEXION_TITLE,
                                                message=scripts.SQL_HELPER_WITHOUT_PROVIDER_ALERT_MESSAGE)
            if new_alert:
                alerts.append(new_alert)

            # ---------------------------------------------
            # Reminder: sql helper without query
            # ---------------------------------------------
            new_alert = self.mixin_create_alert(res_model='es.sql.helper',
                                                domain=[('query_id', '=', False)],
                                                title=scripts.EXTERNAL_CONNEXION_TITLE,
                                                message=scripts.SQL_HELPER_WITHOUT_QUERY_ALERT_MESSAGE)
            if new_alert:
                alerts.append(new_alert)

        return alerts

    @api.multi
    def mixin_compute_tickets(self):
        super(Users, self).mixin_compute_tickets()

        for record in self:
            if not record.email:
                record.mixin_add_ticket(_("This user must have a email."))
            elif not tools.single_email_re.match(record.email):
                record.mixin_add_ticket(_("This user must have a valid email."))
