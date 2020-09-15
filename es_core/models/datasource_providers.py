# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta

import pyodbc
from psycopg2._psycopg import TransactionRollbackError

from odoo import models, fields, api, SUPERUSER_ID, _, tools
from .. import scripts


class SQLProviderGroup(models.Model):
    _name = 'es.sql.provider.group'
    _description = 'no description'

    name = fields.Char(string='Name', required=True)

    # -----------------------------------------------------
    # Constraints
    # -----------------------------------------------------
    _sql_constraints = [
        ('name_uniq', 'unique (name)', scripts.CONSTRAIN_NAME_UNIQUE)
    ]


class SQLProvider(models.Model):
    _name = 'es.sql.provider'
    _description = 'no description'
    _order = 'company_id,name'

    def _default_driver(self):
        drivers = pyodbc.drivers()
        if drivers:
            return drivers[0]

        return False

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    provider_group_id = fields.Many2one('es.sql.provider.group', string='Provider Group')
    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    host = fields.Char(string='Host', required=True, help='For sqlite put here the file path')
    port = fields.Integer(string='Port')
    database = fields.Char(string='Database', required=True)
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    timeout = fields.Integer(string='Timeout (sec)', default=10, required=True)
    driver = fields.Selection(selection=scripts.AVAILABLE_SQL_DRIVERS, string='Driver', required=True,
                              default=_default_driver)
    pool_reset_after = fields.Selection(selection=[(str(minute), str(minute)) for minute in range(5, 65, 5)],
                                        string='Pool Reset (min)', default='60', required=True,
                                        help='Reset connections after this time')
    state = fields.Selection(selection=[(scripts.STATE_CONNECTED, 'Connected'),
                                        (scripts.STATE_DISCONNECTED, 'Disconnected')], string='State',
                             readonly=True, default=scripts.STATE_DISCONNECTED)

    helper_ids = fields.Many2many('es.sql.helper', string='Helpers')

    # FIXME: este campo debe estar en un modulo enfocado a las particularidades de versat
    unit_sql_id = fields.Char('Unit SQL ID')

    # -----------------------------------------------------
    # Constraints
    # -----------------------------------------------------
    _sql_constraints = [
        ('name_uniq', 'unique (name)', scripts.CONSTRAIN_NAME_UNIQUE)
    ]

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.multi
    def name_get(self):
        result = []

        for record in self:
            result.append((record.id, "%s (%s)" % (record.name, record.database)))

        return result

    # -----------------------------------------------------
    # Crons
    # -----------------------------------------------------
    @api.model
    def cron_reset_connections(self):
        pass

    # -----------------------------------------------------
    # Custom
    # -----------------------------------------------------
    def _purify_query_params(self, query_str, query_params):
        if query_params:
            query_str = query_str.lower()
            for param in query_params:
                if param.type == scripts.PREFIX_DATE:
                    sql_value = "CONVERT(DATETIME,'%s 00:00:00', 102)" % param.sql_value if param.sql_value else 'NULL'

                    query_str = query_str.replace('[$%s]' % param.name.lower(), sql_value)
                elif param.type == scripts.PREFIX_LIST:
                    value = eval(param.sql_value)
                    if value:
                        if len(value) == 1:
                            value.append(value[0])

                        value = str(tuple(value))
                    else:
                        value = 'NULL'
                    query_str = query_str.replace('[$%s]' % param.name.lower(), value)
                elif param.type == scripts.PREFIX_BOOL:
                    query_str = query_str.replace('[$%s]' % param.name.lower(),
                                                  '1' if eval(str(param.sql_value)) else '0')
                else:
                    query_str = query_str.replace('[$%s]' % param.name.lower(), param.sql_value or 'NULL')

        return query_str

    def get_handler(self, load_from_pool=True):
        self.ensure_one()

        dns = "DRIVER={%s}" % self.driver
        dns += ";SERVER=%s" % self.host
        # ---------------------------------------
        # if connection if not with SQLITE
        if self.driver.find('sqlite') == -1:
            dns += ";PORT=%s" % self.port
        # ---------------------------------------
        dns += ";DATABASE=%s" % self.database
        dns += ";UID=%s" % self.username
        dns += ";PWD=%s" % self.password
        # dns += "Trusted_Connection=yes;"

        try:
            if not load_from_pool:
                cxn = pyodbc.connect(dns)
                if cxn:
                    scripts.SQL_CONNECTION_HANDLERS[self.id] = cxn
                    self.state = scripts.STATE_CONNECTED
                scripts.SQL_CONNECTION_TIME[self.id] = datetime.now()
                return scripts.SQL_CONNECTION_HANDLERS.get(self.id, False)
            else:
                # open a connection if not open
                if not scripts.SQL_CONNECTION_HANDLERS.get(self.id, False):
                    cxn = pyodbc.connect(dns)
                    if cxn:
                        scripts.SQL_CONNECTION_HANDLERS[self.id] = cxn
                        self.state = scripts.STATE_CONNECTED

                scripts.SQL_CONNECTION_TIME[self.id] = datetime.now()
                return scripts.SQL_CONNECTION_HANDLERS.get(self.id, False)
        except Exception as ex:
            self.state = scripts.STATE_DISCONNECTED
            return False

    @api.model
    def execute(self, query, query_params={}):
        try:
            handler = self.get_handler()
            if handler:
                if isinstance(query, str):
                    query = self._purify_query_params(query, query_params)
                else:
                    query = self._purify_query_params(query.query, query_params)

                cursor = handler.execute(query)
                results = cursor.fetchall()
                columns = [name[0] for name in cursor.description]

                return results, columns
            else:
                return [], []
        except TransactionRollbackError as tre:
            return [], []
        except Exception as ex:
            self.mixin_show_error(ex)

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------
    @api.multi
    def action_test_connection(self):
        self.ensure_one()

        handler = self.get_handler(load_from_pool=False)

        if handler:
            return self.mixin_show_notification(_('Connection'), scripts.CONNECTION_SUCCESSFUL, 'success')
        else:
            self.mixin_show_error(scripts.CONNECTION_BROKEN)


class SQlQuery(models.Model):
    _name = 'es.sql.query'
    _description = 'no description'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name')
    description = fields.Html(string='Description')
    query = fields.Text(string='Query')
    unique_record_field = fields.Char(string='Unique Record Field',
                                      help='This field help you to consolidate data over record with same value'
                                           ' on "unique_record_field" after evaluate this query on different providers.'
                                           ' Please put here the name of the one COLUMN of the query')
    consolidable_field_ids = fields.One2many('es.sql.query.consolidable.field', 'query_id',
                                             string='Consolidable Fields')
    helper_ids = fields.One2many('es.sql.helper', 'query_id', string='SQL Helpers')

    # -----------------------------------------------------
    # Custom
    # -----------------------------------------------------
    def get_query_parameters(self):
        query = self.query
        occurrency = re.findall('.*\[\$(\w*)\].*', query) if query else []
        occurrency = list(dict.fromkeys(occurrency))
        return occurrency

    @api.multi
    def mixin_compute_tickets(self):
        super(SQlQuery, self).mixin_compute_tickets()

        for record in self:
            query_parameters = record.get_query_parameters()

            if query_parameters:
                for param in query_parameters:
                    valid = any([param.startswith(prefix) for prefix in scripts.SQL_VALID_PREFIX])
                    if not valid:
                        record.mixin_add_ticket(scripts.SQL_VALID_PARAM_NAME % param)


class SQlQueryConsolidableField(models.Model):
    _name = 'es.sql.query.consolidable.field'
    _description = 'no description'

    name = fields.Char(string='Field Name')
    math_operation = fields.Selection(selection=[(scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MIN, 'Min'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MAX, 'Man'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_SUM, 'Sum'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_REST, 'Rest'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MULT, 'Mult'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_DIV, 'Div'),
                                                 (scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_AVG, 'Average')]
                                      , string='Math Operation')
    query_id = fields.Many2one('es.sql.query', string='Query')


class SQlHelperParameter(models.Model):
    _name = 'es.sql.helper.parameter'
    _description = 'no description'

    helper_id = fields.Many2one('es.sql.helper', string='Helper')
    name = fields.Char(string='Name', required=True)
    type = fields.Selection(selection=[
        (scripts.PREFIX_STR, _('String')),
        (scripts.PREFIX_INT, _('Integer')),
        (scripts.PREFIX_FLOAT, _('Float')),
        (scripts.PREFIX_BOOL, _('Boolean')),
        (scripts.PREFIX_DATE, _('Date')),
        (scripts.PREFIX_LIST, _('List')),
    ], string='Type', required=True)
    sql_value = fields.Char(string='Value', compute='_compute_sql_value', help='Valid value to replace in query')

    title = fields.Char(string='Title', default='No Title', required=True)

    value_str = fields.Char(string='Value')
    value_int = fields.Integer(string='Value')
    value_float = fields.Float(string='Value')
    value_bool = fields.Boolean(string='Value')
    value_date = fields.Date(string='Value', default=datetime.now().date())

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.model
    def create(self, values):
        if values.get('name', False):
            type_name = values['name'].split('_')
            if len(type_name) >= 2:
                values['type'] = '%s' % type_name[0]

        return super(SQlHelperParameter, self).create(values)

    # -----------------------------------------------------
    # Compute & inverse
    # -----------------------------------------------------
    @api.multi
    @api.depends('type', 'value_str', 'value_int', 'value_float', 'value_bool', 'value_date')
    def _compute_sql_value(self):
        for record in self:
            if record.type == scripts.PREFIX_STR:
                record.sql_value = record.value_str
            if record.type == scripts.PREFIX_INT:
                record.sql_value = str(record.value_int)
            if record.type == scripts.PREFIX_FLOAT:
                record.sql_value = str(record.value_float)
            if record.type == scripts.PREFIX_BOOL:
                record.sql_value = str(record.value_bool)
            if record.type == scripts.PREFIX_DATE:
                if record.value_date:
                    record.sql_value = str(record.value_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
            if record.type == scripts.PREFIX_LIST:
                record.sql_value = str(record.value_str)


class SQlHelper(models.Model):
    _name = 'es.sql.helper'
    _description = 'no description'

    name = fields.Char(string='Name', required=True)
    internal_code = fields.Char(string='Code')
    cron_id = fields.Many2one('ir.cron', string='Schedule Task', ondelete='restrict')
    provider_ids = fields.Many2many('es.sql.provider', string='Providers', required=True)
    query_id = fields.Many2one('es.sql.query', string='Query', required=True)
    query_parameter_ids = fields.One2many('es.sql.helper.parameter', 'helper_id', string='Query Parameters')
    query_return_type = fields.Selection(selection=[(scripts.QUERY_HELPER_RT_SEPARATE, 'Separate'),
                                                    (scripts.QUERY_HELPER_RT_CONSOLIDATE, 'Consolidate')],
                                         string='Query Return Type', required=True,
                                         default=scripts.QUERY_HELPER_RT_SEPARATE)
    interval_number = fields.Integer(string='Interval Number', default=1, help="Repeat every x.")
    interval_type = fields.Selection([(scripts.INTERVAL_MINUTES, 'Minutes'),
                                      (scripts.INTERVAL_HOURS, 'Hours'),
                                      (scripts.INTERVAL_DAYS, 'Days'),
                                      (scripts.INTERVAL_WEEKS, 'Weeks'),
                                      (scripts.INTERVAL_MONTHS, 'Months'),
                                      (scripts.INTERVAL_MANUAL, '..:: MANUAL ::..')],
                                     string='Interval Unit', default=scripts.INTERVAL_DAYS)
    code = fields.Text(string='Python Code', groups='base.group_system',
                       default=scripts.SQL_HELPER_PYTHON_CODE, required=True,
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about python expression is given in the help tab.")

    # -----------------------------------------------------
    # Constrains
    # -----------------------------------------------------
    @api.multi
    @api.constrains('query_return_type')
    def _check_query_return_type(self):
        for record in self:
            if record.query_return_type == scripts.QUERY_HELPER_RT_CONSOLIDATE \
                    and not record.query_id.consolidable_field_ids:
                self.mixin_show_error(scripts.CONNECTION_CONSOLIDABLE_ERROR % record.name)

    # -----------------------------------------------------
    # Onchanges
    # -----------------------------------------------------
    @api.multi
    @api.onchange('query_id')
    def _onchange_query_id(self):
        for record in self:
            record.query_parameter_ids = False

            parameters = record.query_id.get_query_parameters()
            if parameters:
                query_parameter = []
                for name in parameters:
                    type_name = name.split('_')
                    if len(type_name) < 2 or type_name[0] not in scripts.SQL_VALID_PREFIX:
                        record.mixin_show_error(scripts.SQL_VALID_PARAM_NAME)

                    query_parameter.append((0, 0, {
                        'title': name,
                        'name': name,
                        'type': type_name[0],
                    }))

                record.query_parameter_ids = query_parameter

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.model
    def create(self, vals):
        res = super(SQlHelper, self).create(vals)

        model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        for record in res:
            interval_type = record.interval_type
            interval_number = record.interval_number

            if interval_type == scripts.INTERVAL_MANUAL:
                # estos valores son una manera de decir que practicamente el cron se va a ejecutar 1 vez en la vida
                interval_type = scripts.INTERVAL_MONTHS
                interval_number = 9999

            record._onchange_query_id()

            record.cron_id = self.env['ir.cron'].sudo().create({
                'name': 'SQL Helper: %s' % record.name,
                'interval_type': interval_type,
                'interval_number': interval_number,
                'numbercall': -1,
                'doall': True,
                'user_id': SUPERUSER_ID,
                'model_id': model.id,
                'state': 'code',
                'code': record.code
            })

        return res

    @api.multi
    def write(self, vals):
        res = super(SQlHelper, self).write(vals)

        for record in self:
            if record.cron_id:
                record.cron_id.code = record.code

                interval_type = record.interval_type
                interval_number = record.interval_number

                if interval_type == scripts.INTERVAL_MANUAL:
                    # estos valores son una manera de decir que practicamente el cron se va a ejecutar 1 vez en la vida
                    interval_type = scripts.INTERVAL_MONTHS
                    interval_number = 9999

                record.cron_id.interval_type = interval_type
                record.cron_id.interval_number = interval_number

        return res

    @api.multi
    def unlink(self):
        crons = []
        for record in self:
            crons.append(record.cron_id)

        res = super(SQlHelper, self).unlink()

        for cron in crons:
            cron.unlink()

        return res

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------
    @api.multi
    def action_execute(self, other_parameters=[]):
        for record in self:
            if record.cron_id:
                record.cron_id.with_context(OTHER_PARAMETERS=other_parameters).method_direct_trigger()

    # -----------------------------------------------------
    # Custom
    # -----------------------------------------------------
    def custom_query_parameters(self, provider):
        # Redefinir este metodo para injectar en las consultas parametros en el PROVEEDOR
        pass

    @api.model
    def process_data(self):
        def extrat_data(query_record, columns, data):
            results = {}

            # este es el campo que hace unico a cada elemento
            unique_record_field_index = False

            # encontrando el indice de la columna que sera LLAVE en el diccionario
            for index, col_name in enumerate(columns):
                if col_name == query_record.unique_record_field:
                    unique_record_field_index = index

            for row in data:
                if not unique_record_field_index:
                    self.mixin_show_error(
                        scripts.CONNECTION_CONSOLIDABLE_COLUMN_NOT_FOUND % query_record.unique_record_field)

                # 'row[unique_record_field_index]]' es el valor por el cual se van a agrupar los resultados
                results.setdefault(row[unique_record_field_index], {})

                for f in query_record.consolidable_field_ids:
                    for index, col_name in enumerate(columns):
                        if col_name == f.name:
                            col_value = row[index]

                            # definiendo la operacion que se realizara sobre la columna consolidable
                            if f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MIN:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, False)
                                    if not previous_value or previous_value > col_value:
                                        results[row[unique_record_field_index]][col_name] = col_value

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MAX:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, False)
                                    if not previous_value or previous_value < col_value:
                                        results[row[unique_record_field_index]][col_name] = col_value

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_SUM:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, 0)
                                    results[row[unique_record_field_index]][col_name] = previous_value + col_value

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_REST:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, 0)
                                    results[row[unique_record_field_index]][col_name] = previous_value - col_value

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_MULT:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, 0)
                                    results[row[unique_record_field_index]][col_name] = previous_value * col_value

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_DIV:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, 0)
                                    results[row[unique_record_field_index]][col_name] = previous_value / col_value or 1

                            elif f.math_operation == scripts.QUERY_CONSOLIDABLE_MATH_OPERATION_AVG:
                                if isinstance(col_value, (int, float)):
                                    previous_value = results[row[unique_record_field_index]].get(col_name, 0)
                                    results[row[unique_record_field_index]][col_name] = previous_value + col_value

                            break

            return results

        results = {}
        consolidate_results = {}

        params = {p.name: p for p in self.query_parameter_ids}

        # remplazando cualquier nombre de parametro por uno que venga por contexto de mas importancia
        for p in self._context.get('OTHER_PARAMETERS', {}):
            if isinstance(p, SQlHelperParameter):
                params[p.name] = p

        # procesando los datos devueltos
        for provider in self.provider_ids:
            custom_params = self.custom_query_parameters(provider)

            # injectando el ultimo grupo de parametros basados en el provider
            if custom_params:
                for p in custom_params:
                    if isinstance(p, SQlHelperParameter):
                        params[p.name] = p

            # ejecutando la query
            data, columns = provider.execute(self.query_id, query_params=list(params.values()))
            results.setdefault(provider, [])
            if data:
                if self.query_return_type == scripts.QUERY_HELPER_RT_SEPARATE:
                    results[provider] = data
                elif self.query_return_type == scripts.QUERY_HELPER_RT_CONSOLIDATE:
                    data = extrat_data(self.query_id, columns, data)
                    if data:
                        consolidate_results[provider].setdefault({})
                        consolidate_results[provider].update(data)

        # devolviendo la informacion en dependencia de la forma que la solicitaron
        if self.query_return_type == scripts.QUERY_HELPER_RT_SEPARATE:
            return results
        elif self.query_return_type == scripts.QUERY_HELPER_RT_CONSOLIDATE:
            return consolidate_results


class SQLSynchronize(models.TransientModel):
    _name = 'es.sql.synchronize'
    _description = 'no description'

    query_parameter_ids = fields.Many2many('es.sql.helper.parameter', string='Query Parameters')

    # -------------------------------------------------------------------------
    # ORM SECTION
    # -------------------------------------------------------------------------
    @api.model
    def default_get(self, fields):
        res = super(SQLSynchronize, self).default_get(fields)

        res.update({
            'query_parameter_ids': [(6, 0, self.env['es.sql.helper.parameter'].search([], order='type asc').ids)]
        })

        return res

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------
    @api.multi
    def action_execute_update(self):
        self.ensure_one()

        for helper in self.env['es.sql.helper'].search([]):
            helper.action_execute()
