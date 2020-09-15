# -*- encoding: utf-8 -*-
import base64
import logging
import time

from odoo.tools.misc import find_in_path
from . import builders

_logger = logging.getLogger(__name__)


def _get_wkhtmltopdf_bin():
    wkhtmltopdf_bin = find_in_path('wkhtmltopdf')
    if wkhtmltopdf_bin is None:
        raise IOError
    return wkhtmltopdf_bin


# ----------------------------------------------------------------------------------------------------------------------
# PDF Builder
# ----------------------------------------------------------------------------------------------------------------------
class PDFBuilder(builders.Builder):
    def _file_extension(self):
        return 'pdf'

    @staticmethod
    def _build_raw(self, template, report_params=None):
        ViewModel = self.env['ir.ui.view']
        ActionReportModel = self.env['ir.actions.report']

        html = ViewModel.render_template(template, report_params)

        # Ensure the current document is utf-8 encoded.
        html = html.decode('utf-8')

        bodies, html_ids, header, footer, specific_paperformat_args = ActionReportModel._prepare_html(html)
        pdf = ActionReportModel._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=self._context.get('landscape'),
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=self._context.get('set_viewport_size'),
        )

        return base64.b64encode(pdf)

    def _build(self, req, ids, fields, fields_order, results, context=None, report_params=None):
        if report_params is None:
            report_params = {}
        if context is None:
            context = {}
        # Tell QWeb to brand the generated html
        context = dict(context, inherit_branding=True)

        def translate_doc(doc_id, model, lang_field, template):
            ctx = context.copy()
            doc = req.registry[model].browse(req.cr, doc_id, context=ctx)
            qcontext = report_params.copy()
            # Do not force-translate if we chose to display the report in a specific lang
            if ctx.get('translatable') is True:
                qcontext['o'] = doc
            else:
                # Reach the lang we want to translate the doc into
                ctx['lang'] = eval('doc.%s' % lang_field, {'doc': doc})
                qcontext['o'] = req.registry[model].browse(req.cr, doc_id, context=ctx)
            return req.registry['ir.ui.view'].render(req.cr, template, qcontext, context=ctx)

        user = req.env.user
        paper_format = user.company_id.paperformat_id

        report_params.update(
            time=time,
            context_timestamp=lambda t: t,
            translate_doc=translate_doc,
            editable=True,
            user=user,
            res_company=user.company_id,
            company_id=user.company_id,
            fields=fields,
            fields_order=fields_order,
            docs=results,
            context=context,
            web_base_url=req.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
        )
        template = 'es_core.generic_report_detail'

        view_obj = req.env['ir.ui.view'].with_context(context)
        action_report_obj = req.env['ir.actions.report'].with_context(context)

        html = view_obj.render_template(template, report_params)
        # Ensure the current document is utf-8 encoded.
        html = html.decode('utf-8')

        bodies, html_ids, header, footer, specific_paperformat_args = action_report_obj._prepare_html(html)
        pdf_content = action_report_obj._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=context.get('landscape'),
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=context.get('set_viewport_size'),
        )

        return pdf_content
