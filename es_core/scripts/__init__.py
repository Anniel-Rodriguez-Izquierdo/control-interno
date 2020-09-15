# -*- coding: utf-8 -*-

import pyodbc

from odoo import _

# ---------------------------------------------------------
# Global Vars
# ---------------------------------------------------------
DISPLAY_FORMATS = {
    'day': '%d %b %Y',
    'week': 'W%W %Y',
    'month': '%B %Y',
    'year': '%Y',
}

DEFAULT_PRIVATE_ADDRESS_LABEL = _('Private Address')

WORKING_TYPE_MANUAL = 'manual'
WORKING_TYPE_SCHEDULE = 'schedule'

INTERVAL_MINUTES = 'minutes'
INTERVAL_HOURS = 'hours'
INTERVAL_DAYS = 'days'
INTERVAL_WEEKS = 'weeks'
INTERVAL_MONTHS = 'months'
INTERVAL_MANUAL = 'manual'

PREFIX_STR = 'str'
PREFIX_INT = 'int'
PREFIX_FLOAT = 'float'
PREFIX_BOOL = 'bool'
PREFIX_DATE = 'date'
PREFIX_LIST = 'list'

SQL_VALID_PREFIX = [PREFIX_STR, PREFIX_INT, PREFIX_FLOAT, PREFIX_BOOL, PREFIX_DATE, PREFIX_LIST]

UNKNOWN_CODE = 'unknown'
UNKNOWN_LABEL = _('Unknown')
# ---------------------------------------------------------
# SQL Integration
# ---------------------------------------------------------

# En esta variable se guardan las conexiones abiertas a los gestores sql
SQL_CONNECTION_HANDLERS = {}
SQL_CONNECTION_TIME = {}

# Controladores SQL disponibles
AVAILABLE_SQL_DRIVERS = [(driver, driver) for driver in pyodbc.drivers()]

CONNECTION_SUCCESSFUL = _('Connection successful')
CONNECTION_BROKEN = _('Connection broken')

CONNECTION_CONSOLIDABLE_ERROR = _('Query "%s" do not have defined a consolidable field.')
CONNECTION_CONSOLIDABLE_COLUMN_NOT_FOUND = _("Column '%s' not found in query")

QUERY_HELPER_RT_SEPARATE = 'separate'
QUERY_HELPER_RT_CONSOLIDATE = 'consolidate'

QUERY_CONSOLIDABLE_MATH_OPERATION_MIN = 'min'
QUERY_CONSOLIDABLE_MATH_OPERATION_MAX = 'max'
QUERY_CONSOLIDABLE_MATH_OPERATION_AVG = 'avg'
QUERY_CONSOLIDABLE_MATH_OPERATION_SUM = 'sum'
QUERY_CONSOLIDABLE_MATH_OPERATION_REST = 'rest'
QUERY_CONSOLIDABLE_MATH_OPERATION_MULT = 'mult'
QUERY_CONSOLIDABLE_MATH_OPERATION_DIV = 'div'

SQL_HELPER_PYTHON_CODE = _("""# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - base64enconde, base64deconde: useful Python libraries
#  - providers: useful to access to the helper providers
#  - query_result: useful to process data and generate other. 
#           Format: {
#                      'provider ID': [('Col 1', 'Col 2', 'Col 3')...]
#                      'provider ID': [('Col 1', 'Col 2', 'Col 3')...]
#                   }
#  - helper_result: useful to process data and generate other.
#           Format: {
#                      'helper_ID': [('Col 1', 'Col 2', 'Col 3')...]
#                      'helper_ID': [('Col 1', 'Col 2', 'Col 3')...]
#                   }
\n\n\n\n""")

SQL_VALID_PARAM_NAME = _("Param '%s' must start with a valid prefix")

# ---------------------------------------------------------
# BANDERAS
# ---------------------------------------------------------

# Esta bandera es muy util cual un modelo tiene muchas VISTAS de un mismo tipo y deseas usar una en especifico
# ejemlo: en el modulo base hay definido 5 vistas de formulario para el partner y deseas usar una en especifico:
#   * view_partner_simple_form, view_partner_address_form,
#     view_partner_short_form, view_partner_form, res_partner_view_form_private
# ¿como se usa?
#   * <field name='partner_id' context="{
#                                           'form_view_ref': 'base.view_partner_simple_form',
#                                           'tree_view_ref': 'base.view_partner_simple_form',
#                                       }" />
FLAG_XXXX_VIEW_REF = '%s_view_ref'

# Para decir que el campo 'ticket_details' solo accepta ciertos operadores
SEARCH_TICKET_DETAILS_OPERATOR_MESSAGE = _('Field "ticket_details" only accept "=, !=" operator')

# Para marcar el mensaje como una tarea para hacer en el 'Muro'
FLAG_DEFAULT_STARRED = 'default_starred'

# Permite notificar a los partners sobre las modificaciones sobre el objecto
FLAG_MAIL_POST_AUTOFOLLOW = 'mail_post_autofollow'

# Permite enviar la notificacion como un email
FLAG_MAIL_NOTIFY_NO_EMAIL = 'mail_notify_noemail'

# Permite evitar que se asocie la Notificacion como hija del primera Notificacion del Objeto
FLAG_NO_AUTO_THREAD = 'no_auto_thread'

FLAG_MODIFICABLE_STATE = 'modificable_state'

WARNING_TITLE = _('Warning')

# Formato de Direccion para Cuba
CUBAN_FORMAT_ADDRESS = "%(street)s e/ %(street2)s, %(city)s," \
                       " CP: %(zip)s, %(state_name)s, %(country_name)s"

USER_ALERT_TITLE = _('User Alerts')
USER_WITHOUT_EMAIL_ALERT_MESSAGE = _('You have some users without <span class="badge badge-info">EMAILS</span>')

EXTERNAL_CONNEXION_TITLE = _('External Connection Alerts')
SQL_HELPER_WITHOUT_PROVIDER_ALERT_MESSAGE = _(
    'You have some SQL HELPER without <span class="badge badge-info">provider</span>')
SQL_HELPER_WITHOUT_QUERY_ALERT_MESSAGE = _(
    'You have some SQL HELPER without <span class="badge badge-info">query</span>')

# ---------------------------------------------------------
# Priorities
# ---------------------------------------------------------
PRIORITY_NORMAL = '0'
PRIORITY_HIGH = '1'
PRIORITY_URGENT = '2'
PRIORITY_CRITIC = '3'

AVAILABLE_PRIORITIES = [
    (PRIORITY_NORMAL, _('Normal')),
    (PRIORITY_HIGH, _('High')),
    (PRIORITY_URGENT, _('Urgent')),
    (PRIORITY_CRITIC, _('Critic')),
]

# ---------------------------------------------------------
# ESTADOS
# ---------------------------------------------------------
STATE_DRAFT = 'draft'
# se le ha puesto 'open' porque es el estado de APROBADO de un contrato y se ha tomado como referencia
STATE_APPROVED = 'open'
STATE_NOT_DONE = 'not_done'
STATE_JUST_DONE = 'just_done'
STATE_DONE = 'done'
STATE_CLOSED = 'closed'
STATE_SUSPENDED = 'suspended'
STATE_CLOSE = 'close'
STATE_CANCEL = 'cancel'
STATE_CONFIRM = 'confirm'
STATE_CONFIRMED = 'confirmed'
STATE_REFUSE = 'refuse'
STATE_VALIDATE_1 = 'validate1'
STATE_VALIDATE = 'validate'
STATE_RECRUIT = 'recruit'
STATE_NOTIFIED = 'notified'
STATE_RESOLVING = 'resolving'
STATE_CONNECTED = 'connected'
STATE_DISCONNECTED = 'disconnected'

# ---------------------------------------------------------
# CONSTRAINS
# ---------------------------------------------------------
CONSTRAIN_NAME_UNIQUE = _('The name must be unique !')
CONSTRAIN_NAME_CODE_UNIQUE = _('The (name,code) must be unique !')
CONSTRAIN_NAME_TYPE_UNIQUE = _('The (name,type) must be unique !')
CONSTRAIN_TYPE_CODE_UNIQUE = _('The (type,code) must be unique !')
CONSTRAIN_CODE_UNIQUE = _('The code must be unique !')
CONSTRAIN_TYPE_UNIQUE = _('The type must be unique !')

# ---------------------------------------------------------
# CALENDAR
# ---------------------------------------------------------
MONTH_AND_DAYS = {
    '1': {'label': _('January'), 'range': range(1, 32), 'days': 31},
    '2': {'label': _('February'), 'range': range(1, 29), 'days': 28},
    '3': {'label': _('March'), 'range': range(1, 31), 'days': 30},
    '4': {'label': _('April'), 'range': range(1, 31), 'days': 30},
    '5': {'label': _('May'), 'range': range(1, 32), 'days': 31},
    '6': {'label': _('June'), 'range': range(1, 31), 'days': 30},
    '7': {'label': _('July'), 'range': range(1, 32), 'days': 31},
    '8': {'label': _('August'), 'range': range(1, 32), 'days': 31},
    '9': {'label': _('September'), 'range': range(1, 31), 'days': 30},
    '10': {'label': _('October'), 'range': range(1, 32), 'days': 31},
    '11': {'label': _('November'), 'range': range(1, 31), 'days': 30},
    '12': {'label': _('December'), 'range': range(1, 32), 'days': 31},
}

MINUTES = 'minutes'
HOURS = 'hours'
DAYS = 'days'
TIME_UNITS = [(MINUTES, _('Minutes')),
              (HOURS, _('Hours')),
              (DAYS, _('Days'))]
