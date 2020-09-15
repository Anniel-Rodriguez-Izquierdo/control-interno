# -*- coding: utf-8 -*-

import base64
import logging

import werkzeug.urls
from lxml.builder import E
from odoo.addons.mail.models.mail_template import format_tz

import odoo
from odoo import models, fields, api, _, exceptions, tools, SUPERUSER_ID
from odoo.addons.base.models.ir_actions import VIEW_TYPES
from odoo.tools.image import image_data_uri
from .. import scripts

_logger = logging.getLogger('')


def fix_image_data_uri(base64_source):
    if base64_source:
        return image_data_uri(base64_source)
    else:
        return ''


# ----------------------------------------------------------------------------------------------------------------------
# Sticky Note Item
# ----------------------------------------------------------------------------------------------------------------------
class Ticket(models.AbstractModel):
    _name = 'base.ticket'
    _description = 'no description'

    # -------------------------------------------------------------------------
    # FIELDS SECTION
    # -------------------------------------------------------------------------
    model_id = fields.Many2one('base', string='Model')
    detail = fields.Html(string='Detail')


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    # -------------------------------------------------------------------------
    # FIELDS SECTION
    # -------------------------------------------------------------------------
    ticket_ids = fields.One2many('base.ticket', 'model_id', string='Tickets', compute='mixin_compute_tickets')
    ticket_details = fields.Html(string='Ticket Details',
                                 compute='mixin_compute_ticket_details',
                                 search='mixin_search_ticket_details')

    # -------------------------------------------------------------------------
    # Default Views SECTION
    # -------------------------------------------------------------------------
    @api.model
    def _get_default_dashboard_view(self):
        # Generates a default dashboard view containing default sub graph and pivot views.
        #
        # :returns: a dashboard view as an lxml document
        # :rtype: etree._Element
        dashboard = E.dashboard()
        # dashboard.append(E.view(type="graph"))
        # dashboard.append(E.view(type="pivot"))
        return dashboard

    # -------------------------------------------------------------------------
    # COMPUTE SECTION
    # -------------------------------------------------------------------------
    @api.multi
    @api.depends('ticket_ids')
    def mixin_compute_ticket_details(self):
        for record in self:
            if record.ticket_ids:
                record.ticket_details = "%s" % ("".join([item.detail for item in record.ticket_ids]))
            else:
                record.ticket_details = False

    def mixin_search_ticket_details(self, operator, value):
        assert operator in ['=', '!='], scripts.SEARCH_TICKET_DETAILS_OPERATOR_MESSAGE

        if ("%s%s" % (operator, value)) in ['=True', '=1', '!=False']:
            operator = 'in'
        else:
            operator = 'not in'

        records = self.env[self._name].search([]).filtered(lambda record: record.ticket_ids)
        return [('id', operator, records.ids)]

    # -------------------------------------------------------------------------
    # CUSTOM SECTION
    # -------------------------------------------------------------------------
    def mixin_get_logger(self):
        return _logger

    def mixin_get_image(self, module_name='base', relative_path='static/src/img', image_name='avatar.png'):
        # Permite cargar una imagen que este dentro de un modulo
        # :param module_name:
        # :param relative_path:
        # :param image_name:
        # :return:
        img_path = odoo.modules.get_module_resource(module_name, relative_path, image_name)
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
            if image:
                image = tools.image_colorize(image)
                return tools.image_resize_image_big(base64.b64encode(image))

        return None

    def mixin_get_image_as_base_64(self, module_name='base', relative_path='static/src/img', image_name='avatar.png'):
        # Permite cargar el base64 de una imagen que este dentro de un modulo
        # :param module_name:
        # :param relative_path:
        # :param image_name:
        # :return:
        img_path = odoo.modules.get_module_resource(module_name, relative_path, image_name)
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
            if image:
                return tools.image_resize_image_big(base64.b64encode(image))

        return None

    # -----------------------------------------------------
    def mixin_show_error_activation(self, msg):
        raise exceptions.AccessError(_('Some activation permissions are denied: \n %s') % msg)

    def mixin_show_error(self, msg):
        raise exceptions.ValidationError(msg)

    def mixin_show_notification(self, title, message, message_type, next_action=False):
        action = self.env.ref('es_core.action_view_wizard_notification').read()[0]
        action['name'] = title
        action['context'] = dict(
            default_message=message,
            default_message_type=message_type,
            default_next_action=next_action,
        )
        return action

    def mixin_redirect_to(self, action_id, button_title, message):
        action = self.env.ref(action_id)
        raise exceptions.RedirectWarning(message, action.id, button_title)

    # -----------------------------------------------------
    def mixin_get_config(self, key, default=None, _eval=True):
        # Permite acceder al valor de una configuracion
        # :param key:
        # :param default:
        # :return:
        if _eval:
            return eval(self.env['ir.config_parameter'].sudo().get_param(key, str(default)))
        else:
            return self.env['ir.config_parameter'].sudo().get_param(key, str(default))

    def mixin_set_config(self, key, value=None):
        # Permite cambiar el valor de una configuracion
        # :param key:
        # :param value:
        # :return:
        return self.env['ir.config_parameter'].sudo().set_param(key, value)

    # -----------------------------------------------------
    def mixin_fire_action(self, action_data):
        # Este metodo te permite construir una accion de una manera mas practica permitiendo especificar
        # las vistas que deseas cargar usando su XML_ID
        # Ejemplo:
        #     Este es solo un ejemplo pero tu puedes crear cualquier tipo de accion: act_window, report, ...
        #     {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Caseload'),
        #         'view_mode': 'tree,form',
        #         'res_model': 'my.model',
        #         'view_id': 'module.view_xml_id',
        #         'search_view_id': 'module.view_xml_id',
        #         'views': [
        #             ('module.view_xml_id', 'tree'),
        #             ('module.view_xml_id', 'form')
        #          ],
        #         'context': {},
        #         'domain': [],
        #         'res_id': 1234567890,
        #         'target': 'new'
        #     }
        # :param action_data:
        # :return:
        self.ensure_one()

        if 'view_id' in action_data:
            view = self.env.ref(action_data['view_id'])
            action_data['view_id'] = (view.id, view.name)
        if 'search_view_id' in action_data:
            view = self.env.ref(action_data['search_view_id'])
            action_data['search_view_id'] = (view.id, view.name)
        # ----------------------------------------------------------------
        if 'views' in action_data:
            views_computed = []
            for view in action_data['views']:
                id_view = self.env.ref(view[0]).id
                type_view = view[1]
                if (type_view, type_view.capitalize()) in VIEW_TYPES:
                    views_computed.append((id_view, type_view))
            action_data['views'] = views_computed
        # ----------------------------------------------------------------
        if 'domain' in action_data:
            action_data['domain'] = str(action_data['domain'])
        # ----------------------------------------------------------------
        return action_data

    def mixin_check_groups(self, xml_groups=None, in_all=False):
        # Permite verificar si un usuario tiene 1 o todos los grupos especificados
        # :param xml_groups:
        # :param in_all:
        # :return:
        if xml_groups is None:
            xml_groups = []
        matches = 0
        for xml_id in xml_groups:
            if self.env.user.has_group(xml_id):
                matches += 1

        return matches == len(xml_groups) if in_all else matches != 0

    def mixin_generate_url(self, record, view_type):
        base_url = self.mixin_get_config('web.base.url',
                                         'http://localhost:%s' % tools.config.options.get('http_port'),
                                         False)
        return werkzeug.urls.url_join(
            base_url, '#home&%s' % werkzeug.urls.url_encode({
                'db': self.env.cr.dbname,
                'id': record.id,
                'model': record._name,
                'view_type': view_type,
            }))

    # -----------------------------------------------------
    def mixin_convert_report_in_attachment(self, xml_id):
        # Permite generar un Attachment a partir del xml_id de una accion de reporte
        # :param xml_id:
        # :return:
        self._context['format_tz'] = lambda dt, tz=False, format=False, context=self._context: format_tz(self.env,
                                                                                                         dt, tz, format)
        # -----------------------------------------------------------
        # la logica de este metodo es original del modelo mail.template en el metodo generate_mail()
        # pero fue adaptado para generar un attachment a partir del xml_id de un reporte
        # -----------------------------------------------------------
        report = self.env.ref(xml_id)
        report_name = report.display_name
        report_service = report.report_name
        # -----------------------------------------------------------
        if report.report_type not in ['qweb-html', 'qweb-pdf']:
            self.show_error(_('Unsupported report type %s found.') % report.report_type)

        result, report_format = report.render_qweb_pdf([report.id])
        # -----------------------------------------------------------
        result = base64.b64encode(result)
        if not report_name:
            report_name = 'report.' + report_service
        ext = "." + report_format
        if not report_name.endswith(ext):
            report_name += ext
        # -----------------------------------------------------------
        return self.env['ir.attachment'].create({
            'name': report_name,
            'datas_fname': report_name,
            'datas': result,
            'res_model': 'mail.mail'
        })

    def mixin_render_template(self, template_xml_id=None, params=None):
        # Permite compilar una plantilla qweb y obtener el codigo html
        # :param template_xml_id:
        # :param params:
        # :param links:
        # :return:
        if params is None:
            params = {}
        body = ''
        if template_xml_id:
            ActionReport = self.env['ir.actions.report']
            body = ActionReport.render_template(template_xml_id, values=params)
            body = body.decode('utf-8')
            # Ensure the current document is utf-8 encoded.
            body = tools.html_sanitize(body)
        return body

    def mixin_notify_message(self, follow_object=None, subject=None, body=None, mark_as_todo=False,
                             autofollow=True, mail_notify_noemail=False,
                             partner_ids=None, author_id=None,
                             attachment_ids=None):
        # Importante: para usar este metodo el modelo debe extender de 'mail.thread'
        # :param follow_object: objecto sobre el cual se registrara el mensaje
        # :param subject: titulo del mensaje
        # :param body: mensaje
        # :param mark_as_todo: marcarlo como una tarea para hacer en el 'Muro'
        # :param autofollow: permite notificar a los partners sobre las modificaciones sobre el objecto
        # :param mail_notify_noemail: Permite enviar la notificacion como un email:
        #                             es usado en el metodo '_notify' en el model 'mail.notification'
        # :param partner_ids:
        # :param author_id: por defecto el autor del mensaje sera el usuario logueado a menos que se especifique otro
        # :param attachment_ids:
        # :return: El mensaje generado o False
        if partner_ids is None:
            partner_ids = []
        if follow_object:
            context = {}
            # -----------------------------------------------------------
            if mark_as_todo:
                context[scripts.FLAG_DEFAULT_STARRED] = True
            if autofollow:
                context[scripts.FLAG_MAIL_POST_AUTOFOLLOW] = True
            context[scripts.FLAG_MAIL_NOTIFY_NO_EMAIL] = mail_notify_noemail
            context[scripts.FLAG_NO_AUTO_THREAD] = True
            # -----------------------------------------------------------
            params = {}
            # -----------------------------------------------------------
            if partner_ids:
                params['partner_ids'] = partner_ids
            if author_id:
                params['author_id'] = author_id
            if attachment_ids:
                params['attachment_ids'] = attachment_ids
            # -----------------------------------------------------------
            msg_id = False

            if follow_object._name == 'res.partner':
                user = self.env['res.users'].search([('partner_id', '=', follow_object.id)])

                if not user.email or (user.alias_name and user.alias_domain):
                    msg_id = follow_object. \
                        with_env(self.env(user=SUPERUSER_ID)). \
                        with_context({scripts.FLAG_DEFAULT_STARRED: True}). \
                        message_post(subject=_('It is urgent'), body=_("Some important message don't have been "
                                                                       "notified to you because you don't"
                                                                       " have a valid email"))
                else:
                    msg_id = follow_object. \
                        with_env(self.env(user=user.id)). \
                        with_context(context). \
                        message_post(subject=subject, body=body, **params)
            else:
                can_write = follow_object.check_access_rights('write', raise_exception=False)

                env = self.env
                if not can_write:
                    env = self.env(user=SUPERUSER_ID)

                msg_id = follow_object. \
                    with_env(env). \
                    with_context(context). \
                    message_post(subject=subject, body=body, **params)
            # -----------------------------------------------------------
            return msg_id
        return False

    def mixin_send_simple_mail(self, _from, _to=None, values=None, attachment_ids=None, template_xml_id=False):
        # Permite enviar un correo usando una plantilla definida con el modelo 'mail.template'
        #
        # :param _from:
        # :param _to:
        # :param values:
        # :param attachment_ids:
        # :param template_xml_id:
        # :return:

        if attachment_ids is None:
            attachment_ids = []
        if values is None:
            values = {}
        if _to is None:
            _to = []

        def _field_selection_label(field_name, field_value):
            return dict(self._fields[field_name].selection).get(field_value, False)

        template = self.env.ref(template_xml_id)

        values.update(
            email_from=_from,
            email_to=_to,
            image_data_uri=fix_image_data_uri,
            field_selection_label=_field_selection_label,
            generate_url=self.mixin_generate_url,
            config_parameter=self.mixin_get_config,
            user=self.env.user,
            attachment_ids=attachment_ids,
        )

        template.with_context(values).send_mail(self.id, email_values=values)

    def mixin_send_mail(self, _from, _to=None, subject='Your subject here', attachment_ids=False,
                        template_xml_id=False, params=None):
        # Permite enviar un correo
        # :param _from: direccion de correo de quien lo envia
        # :param _to: lista de direccionnes de correos destinatarios: ej: ['email','email 2']
        # :param subject: asunto del correo
        # :param attachment_ids: adjuntos
        # :param template_xml_id: plantilla qweb que se enviara por correo
        # :param params: diccionario de valores para compilar la plantilla
        # :return: mensaje generado
        # -----------------------------------------------------------
        if params is None:
            params = {}
        if _to is None:
            _to = []
        body = self.mixin_render_template(template_xml_id, params)
        # -----------------------------------------------------------
        # obj_mail_server = self.pool.get('ir.mail_server')
        # msg = obj_mail_server.build_email(_from, _to, subject, body, attachments=attachments, subtype='html')
        # obj_mail_server.send_email(self.env.cr, self.env.uid, msg)
        # -----------------------------------------------------------
        mail_data = {
            'email_from': _from,
            'email_to': ', '.join(_to),
            'subject': subject,
            'body': body,
            'body_html': body,
            'type': 'email',
            'state': 'outgoing',
            'auto_delete': True
        }
        if attachment_ids:
            mail_data['attachment_ids'] = [(6, 0, attachment_ids)]
        # -----------------------------------------------------------
        self.env['mail.mail'].create(mail_data)

    # -----------------------------------------------------
    @api.multi
    def mixin_add_ticket(self, message=False):
        # Este metodo lo debes usar cuando deseas mostrar
        # informacion de relevancia temporal en la parte superior del formulario
        # :param message:
        # :return: nada
        if message:
            ticket = self.env['base.ticket']
            for record in self:
                record.ticket_ids |= ticket.new({
                    'detail': message,
                })

    def mixin_create_alert(self, res_model, domain, title, message, alert_icon="fa fa-bell", action_xml_id=False):
        # Permite crear una alerta para mostrar en el Systray menu si y solo si se encuentran RECORDS que coincidan con
        # en DOMINIO especificado
        # :param res_model: Modelo que se va a cargar cuando se de click en la alerta
        # :param domain: Dominio para hacer la busqueda sobre el modelo 'res_model'
        # :param title: Titulo de la alerta
        # :param message: Mensaje de la alerta
        # :param alert_icon: Icono de la alerta
        # :param action_xml_id: Accion que se ejecutara cuando el usuario de click sobre la alerta
        # :return:
        if isinstance(domain, list) and self.env[res_model].search_count(domain):
            return dict(
                icon=alert_icon,
                title=title,
                message=message,
                res_model=res_model,
                domain=str(domain),
                action=action_xml_id
            )

        return False

    def mixin_create_simple_alert(self, title, message, alert_icon="fa fa-bell", action_xml_id=False):
        # Permite crear una alerta para mostrar en el Systray menu si y solo si se encuentran RECORDS que coincidan con
        # en DOMINIO especificado
        # :param res_model: Modelo que se va a cargar cuando se de click en la alerta
        # :param domain: Dominio para hacer la busqueda sobre el modelo 'res_model'
        # :param title: Titulo de la alerta
        # :param message: Mensaje de la alerta
        # :param alert_icon: Icono de la alerta
        # :param action_xml_id: Accion que se ejecutara cuando el usuario de click sobre la alerta
        # :return:
        return dict(
            icon=alert_icon,
            title=title,
            message=message,
            res_model=False,
            domain=False,
            action=action_xml_id
        )

    # -------------------------------------------------------------------------
    # Override this methods
    # -------------------------------------------------------------------------
    @api.multi
    def mixin_compute_tickets(self):
        # Este metodo debe ser sobreescrito en las clases hijas y usar ademas 'mixin_add_ticket' para registrar
        # Tickets
        # :return: nada
        pass

    def mixin_form_view_readonly_domain(self):
        # La vista formulario sera Solo-Lectura si cumple con este DOMINIO
        # :return: expresion de dominio or False
        return False

    def mixin_kanban_view_readonly(self):
        # La vista kanban sera Solo-Lectura para evitar que arrastren ELEMENTOS entre columnas cuando
        # la vista esta agrupada
        # :return: True or False
        return False
