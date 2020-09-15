# -*- encoding: utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json

import locale
from datetime import datetime
from operator import itemgetter

from lxml import etree

import odoo.tools as tools

try:
    import xlwt
    from xlwt import *
except ImportError:
    xlwt = None

# ----------------------------------------------------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------------------------------------------------
KEY_SELECTED_ITEMS = 'only_items_selected'
KEY_VISIBLE_ITEMS = 'only_items_visible'
KEY_ALL_ITEMS = 'all_items'


# ----------------------------------------------------------------------------------------------------------------------
# Builder
# ----------------------------------------------------------------------------------------------------------------------
class Builder(object):
    def _parse_node(self, root_node):
        # Documentation:
        # This method return the proper ordered fields based on xml definition of view .
        result = []
        for node in root_node:
            field_name = node.get('name')
            if not eval(str(node.attrib.get('invisible', False)), {'context': self.context}):
                if node.tag == 'field':
                    if field_name in self.groupby:
                        continue
                    result.append(field_name)
                else:
                    result.extend(self._parse_node(node))
        return result

    def _parse_string(self, view):
        # Documentation:
        # This method get the active view and return the valid fields in proper order.
        try:
            dom = etree.XML(view.encode('utf-8'))
        except Exception:
            dom = etree.XML(view)
        return self._parse_node(dom)

    def _format_data(self, fields, fields_order, results):
        # Documentation:
        # This method is used for processing each field to apply proper format to them.
        for line in results:
            count = -1
            for f in fields_order:
                float_flag = 0
                count += 1
                if f in fields:
                    if fields[f]['type'] == 'many2one' and line[f]:
                        if not line.get('__group'):
                            line[f] = line[f][1]
                    # ------------------------------
                    if fields[f]['type'] == 'selection' and line[f]:
                        for key, value in fields[f]['selection']:
                            if key == line[f]:
                                line[f] = value
                                break
                    # ------------------------------
                    if fields[f]['type'] in ('one2many', 'many2many') and line[f]:
                        line[f] = '( ' + tools.ustr(len(line[f])) + ' )'
                    # ------------------------------
                    if fields[f]['type'] == 'float' and line[f]:
                        precision = (('digits' in fields[f]) and fields[f]['digits']) or 2
                        prec = '%.' + str(precision) + 'f'
                        line[f] = prec % (line[f])
                        float_flag = 1
                    # ------------------------------
                    if fields[f]['type'] == 'date' and line[f]:
                        new_d1 = line[f]
                        if not line.get('__group'):
                            format = str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))
                            d1 = datetime.strptime(line[f], '%Y-%m-%d')
                            new_d1 = d1.strftime(format)
                        line[f] = new_d1
                    # ------------------------------
                    if fields[f]['type'] == 'time' and line[f]:
                        new_d1 = line[f]
                        if not line.get('__group'):
                            format = str(locale.nl_langinfo(locale.T_FMT))
                            d1 = datetime.strptime(line[f], '%H:%M:%S')
                            new_d1 = d1.strftime(format)
                        line[f] = new_d1
                    # ------------------------------
                    if fields[f]['type'] == 'datetime' and line[f]:
                        new_d1 = line[f]
                        if not line.get('__group'):
                            format = str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')) + ' ' + str(
                                locale.nl_langinfo(locale.T_FMT))
                            d1 = datetime.strptime(line[f], '%Y-%m-%d %H:%M:%S')
                            new_d1 = d1.strftime(format)
                        line[f] = new_d1

    def _format_filters(self, req, model_name, fields, filters):
        results = []
        # ------------------------------
        valid_fields = fields.copy()
        # ------------------------------
        for filter in filters:
            f_name = filter[0]
            f_value = filter[2]
            # ------------------------------
            if not f_name in valid_fields:
                # if left expression is a path like: field_id.field_id....
                model = req.env[model_name].browse()
                f_name = f_name[f_name.rfind('.') + 1:]
                valid_fields[f_name] = model.fields_get()[f_name]
            # ------------------------------
            if not 'relation' in valid_fields[f_name]:
                results.append({
                    'string': valid_fields[f_name]['string'],
                    'value': f_value
                })
            else:
                relation = valid_fields[f_name]['relation']
                domain = ['id', '=', f_value]
                item = req.session.model(relation).read(f_value, False, req.context)
                if item:
                    results.append({
                        'string': valid_fields[f_name]['string'],
                        'value': item['display_name']
                    })
        return results

    def create(self, req, ids, model_name, domain, context=None, report_params={}):
        # Documentation:
        # Only for internal purpose.
        #   This method retrieve data based on "IDS, MODEL, CONTEXT, GROUP BY".
        #   The client widget send this info.
        if not context:
            context = {}
        if not report_params:
            report_params = {}
        # ------------------------------
        report_params.update(model=model_name)
        # ------------------------------
        self.context = context
        self.view_id = context.get('view_id', [])

        self.groupby = context.get('group_by', [])
        if self.groupby:
            field_names = []
            for data in self.groupby:
                data = eval(data)
                group_by = data.get('group_by', False)
                if group_by:
                    field_names.append(group_by)
            self.groupby = field_names
            self.context['group_by'] = field_names

        self.groupby_no_leaf = context.get('group_by_no_leaf', False)
        # ------------------------------
        model = req.env[model_name]
        # ------------------------------
        arch = model.fields_view_get(view_id=self.view_id, view_type='tree')['arch']
        fields = model.fields_get()
        fields_order = self.groupby + self._parse_string(arch)
        # ------------------------------
        if self.groupby:
            rows = []

            def get_groupby_data(groupby=[], domain=[]):
                records = model.read_group(domain, fields_order, groupby, 0, None)
                for rec in records:
                    rec['__group'] = True
                    rec['__no_leaf'] = self.groupby_no_leaf
                    rec['__grouped_by'] = groupby[0] if (isinstance(groupby, list) and groupby) else groupby
                    for f in fields_order:
                        if f not in rec:
                            rec.update({f: False})
                        elif isinstance(rec[f], tuple):
                            rec[f] = rec[f][1]
                    rows.append(rec)
                    inner_groupby = (rec.get('__context', {})).get('group_by', [])
                    inner_domain = rec.get('__domain', [])
                    if inner_groupby:
                        get_groupby_data(inner_groupby, inner_domain)
                    else:
                        if self.groupby_no_leaf:
                            continue
                        children = model.search(inner_domain)
                        res = children.read(fields_order)
                        res.sort(key=lambda x: ids.index(x['id']))
                        rows.extend(res)

            dom = [('id', 'in', ids)]
            if self.groupby_no_leaf and len(ids) and not ids[0]:
                dom = domain or []

            get_groupby_data(self.groupby, dom)
        else:
            rows = model.search([('id', 'in', ids)]).read(fields.keys())
            ids2 = map(itemgetter('id'), rows)
            # getting the ids from read result
            if ids != ids2:
                # sorted ids were not taken into consideration for print screen
                rows_new = []
                for id in ids:
                    rows_new += [elem for elem in rows if elem['id'] == id]
                rows = rows_new
        # ------------------------------
        # apply proper format to each field on objects
        self._format_data(fields, fields_order, rows)
        # ------------------------------
        report_params.update(
            format_filters=self._format_filters(req, model_name, fields, domain)
        )
        # ------------------------------
        content = self._build(req, ids, fields, fields_order, rows, context, report_params)
        return content, self._file_extension()

    def _file_extension(self):
        # Documentation:
        #    Child class must implement this method.
        raise NotImplementedError()

    def _build(self, req, ids, fields, fields_order, rows, context):
        # Documentation:
        #    Child class must implement this method.
        raise NotImplementedError()
