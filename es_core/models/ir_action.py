# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


# Para permitir que en la accion puedan definir un nuevo tipo de vista: DASHBOARD
class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('dashboard', "Dashboard")])


# Esta implementacion es importante para poder injectarle mas variables a las Acciones de Servidor y puedan ser
# usadas en la expresion de python de la accion
class ServerActions(models.Model):
    _inherit = 'ir.actions.server'

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.model
    def run_action_code_multi(self, action, eval_context=None):
        safe_eval(action.sudo().code.strip(), eval_context, mode="exec", nocopy=True)  # nocopy allow to return 'action'

        if 'action' in eval_context:
            return eval_context['action']
        else:
            return {
                'result_text': eval_context['result_text'],
                'result_numeric': eval_context['result_numeric'],
                'result_boolean': eval_context['result_boolean'],
            }

    @api.model
    def _get_eval_context(self, action=None):
        eval_context = super(ServerActions, self)._get_eval_context(action)

        # Agregando la variable 'result' para que la accion pueda retornar un valor en la expresion python
        eval_context['result_text'] = False
        eval_context['result_numeric'] = False
        eval_context['result_boolean'] = False

        # agregando la variable 'query_result' para que se tenga acceso
        # a los valores de una consulta en la expresion python
        sql_helper = self.env['es.sql.helper'].search([('cron_id.ir_actions_server_id', '=', self.id)], limit=1)
        if sql_helper:
            eval_context['providers'] = sql_helper.provider_ids

            query_result = sql_helper.process_data()
            eval_context['query_result'] = query_result if query_result else []

            # aqui quito un poco de variables que no quiero que el programador acceda a ellas
            if 'uid' in eval_context:
                eval_context.pop('uid')

            if 'user' in eval_context:
                eval_context.pop('user')

            if 'model' in eval_context:
                eval_context.pop('model')

            if 'Warning' in eval_context:
                eval_context.pop('Warning')

            if 'record' in eval_context:
                eval_context.pop('record')

            if 'records' in eval_context:
                eval_context.pop('records')

            if 'log' in eval_context:
                eval_context.pop('log')

        return eval_context
