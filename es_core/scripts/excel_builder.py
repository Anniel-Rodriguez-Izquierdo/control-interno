# -*- encoding: utf-8 -*-

from io import BytesIO

import odoo.tools as tools
from odoo import _

try:
    import xlwt
    from xlwt import *
except ImportError:
    xlwt = None

from . import builders


# ----------------------------------------------------------------------------------------------------------------------
# EXCEL Builder
# ----------------------------------------------------------------------------------------------------------------------
class ExcelBuilder(builders.Builder):
    def _file_extension(self):
        return 'xls'

    def _build(self, req, ids, fields, fields_order, results, context, report_params={}):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        # ------------------------------
        headerTokenStyle = xlwt.easyxf('font: bold on; align: wrap yes, vert centre, horiz right')
        colNameStyle = xlwt.easyxf(
            'font: bold on; align: wrap yes, vert centre, horiz left; pattern: pattern solid, fore_colour gray25;')
        # ------------------------------
        field_style = xlwt.easyxf('align: wrap yes')
        # ------------------------------
        company = report_params['company'].name if report_params.get('company', False) else ''

        worksheet.write(3, 0, _('Company:'), headerTokenStyle)
        worksheet.write(3, 1, tools.ustr(company))
        worksheet.write(4, 0, _('Author:'), headerTokenStyle)
        worksheet.write(4, 1, tools.ustr(report_params.get('author', '')))
        worksheet.write(5, 0, _('Date:'), headerTokenStyle)
        worksheet.write(5, 1, tools.ustr(report_params.get('date', '')))
        worksheet.write(6, 0, _('Filters:'), headerTokenStyle)
        # ------------------------------
        filters = ''
        applied_filters = report_params.get('format_filters', [])
        for filter in applied_filters:
            filters += '{0}: {1}, '.format(filter['string'], filter['value'])
        worksheet.write_merge(6, 6, 1, 3, filters)
        # ------------------------------
        col_name_row = 8
        for i, f in enumerate(fields_order):
            value = tools.ustr(fields[f]['string'] or '')

            worksheet.write(col_name_row, i, value, colNameStyle)

            # se multiplica por 8 porque se usan 8 pixeles para dibujar un caracter
            _current_with = worksheet.col(i).width
            if len(value) * 8 > _current_with:
                worksheet.col(i).width = len(value) * 8
        # ------------------------------
        # to not repeat value in column who represent groups
        fields_grouped = []
        row_value_start = col_name_row + 1
        for row_index, line in enumerate(results):
            for col_index, f in enumerate(fields_order):
                # Prevent empty labels in groups
                if f == line.get('__grouped_by') and line.get('__group') and not line[f]:
                    value = line[f] = 'Undefined'
                # ------------------------------
                if line[f] is not None:
                    value = tools.ustr(line[f] or '')
                else:
                    value = '/'
                # ------------------------------
                if line.get('__group'):
                    fields_grouped.append(f)
                    worksheet.write(row_value_start + row_index, col_index, value, field_style)
                    break
                else:
                    if f not in fields_grouped:
                        worksheet.write(row_value_start + row_index, col_index, value, field_style)
        # ------------------------------
        fp = BytesIO()
        workbook.save(fp)

        fp.seek(0)
        data = fp.read()
        fp.close()
        # ------------------------------
        return data
