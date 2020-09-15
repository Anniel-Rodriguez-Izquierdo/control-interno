# -*- coding: utf-8 -*-

from uuid import uuid4

from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    guide_ids = fields.One2many('syap.ic.guide', 'company_id', 'Guides')


class Component(models.Model):
    _name = 'syap.ic.component'
    _description = 'no description'
    _order = 'sequence asc'

    sequence = fields.Integer('Sequence', default=0, required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)
    aoi_ids = fields.Many2many('syap.ic.area_of_interest', string='Area of Interests',
                               default=lambda self: self.env.ref('syap_control_interno.data_aoi_common'))
    topic_ids = fields.Many2many('syap.ic.topic', string='Topics')


class AreaOfInterest(models.Model):
    _name = 'syap.ic.area_of_interest'
    _description = 'no description'
    _order = 'sequence asc'

    sequence = fields.Integer('Sequence', default=0, required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)


class Topic(models.Model):
    _name = 'syap.ic.topic'
    _description = 'no description'
    _order = 'sequence asc'

    sequence = fields.Integer('Sequence', default=0, required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)


class Explanation(models.Model):
    _name = 'syap.ic.question.explanation'
    _description = 'no description'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)


class AutoControlGuide(models.Model):
    _name = 'syap.ic.guide'
    _description = 'no description'

    def _default_parent_guide_id(self):
        current_company = self.env.user.company_id
        return str([('company_id', '=', current_company.parent_id.id)])

    parent_guide_id = fields.Many2one('syap.ic.guide', 'Parent Guide', domain=_default_parent_guide_id)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True)
    name = fields.Char('Title', required=True)
    question_ids = fields.One2many('syap.ic.guide.question', 'guide_id', 'Questions')

    advance_form_view = fields.Html(compute='_compute_advance_form_view')

    # -----------------------------------------------------
    # Onchange & Computes
    # -----------------------------------------------------
    @api.onchange('parent_guide_id')
    def onchange_parent_guide_id(self):
        for record in self:
            RemovedPhantomItemsEnv = self.env['syap.ic.guide.question']
            for question in record.question_ids:
                if not question.company_origin or question.company_origin == question.company_owner:
                    RemovedPhantomItemsEnv |= question

            record.question_ids = RemovedPhantomItemsEnv

            if record.parent_guide_id.id:
                items = []
                for question in record.parent_guide_id.question_ids:
                    items.append((0, 0, {
                        'guide_id': record.id,
                        'component_id': question.component_id.id,
                        'aoi_id': question.aoi_id.id,
                        'topic_id': question.topic_id.id,
                        'name': question.name,
                        'company_origin': question.company_origin,
                    }))

                record.question_ids = items

    @api.depends('question_ids')
    def _compute_advance_form_view(self):
        for record in self:
            components = {}
            for question in record.question_ids:
                # registro el componente-------------------
                components.setdefault(question.component_id.code, {
                    'title': question.component_id.name,
                    'topics': {},
                })
                # registro el topico-----------------------
                components[question.component_id.code]['topics'].setdefault(question.topic_id.code, {
                    'title': question.topic_id.name,
                    'questions': [],
                })
                # registro la pregunta---------------------
                components[question.component_id.code]['topics'][question.topic_id.code]['questions'].append(question)

            record.advance_form_view = self.mixin_render_template('syap_control_interno.autocontrol_guide_template', {
                'components': components
            })


class AutoControlGuideQuestion(models.Model):
    _name = 'syap.ic.guide.question'
    _description = 'no description'
    _order = 'component_id asc, topic_id asc, sequence asc'

    guide_id = fields.Many2one('syap.ic.guide', 'Guide', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=0, required=True)
    component_id = fields.Many2one('syap.ic.component', 'Component', required=False)
    aoi_id = fields.Many2one('syap.ic.area_of_interest', 'Area of Interest', required=True)
    topic_id = fields.Many2one('syap.ic.topic', 'Topic', required=True)
    name = fields.Text('Question', required=False)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)
    response = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Response')
    response_explanation = fields.Many2many('syap.ic.question.explanation', string='Explanation')

    company_origin = fields.Char('Origin', help='Only for internal use')
    company_owner = fields.Char(related='guide_id.company_id.name', store=True, help='Only for internal use')

    line_ids = fields.One2many('syap.ic.guide.question.line', 'question_id', string='Lines')

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    def create(self, vals_list):
        res = super(AutoControlGuideQuestion, self).create(vals_list)

        for record in res:
            if not record.company_origin:
                record.company_origin = record.guide_id.company_id.name
            if not record.company_owner:
                record.company_owner = record.guide_id.company_id.name

    # -----------------------------------------------------
    # Onchanges
    # -----------------------------------------------------
    @api.onchange('component_id')
    def _onchange_component_id(self):
        self.ensure_one()

        d_aoi_ids = [('id', 'in', self.component_id.aoi_ids.ids)] if self.component_id.id else []
        d_topic_id = [('id', 'in', self.component_id.topic_ids.ids)] if self.component_id.id else []

        return {
            'domain': {
                'aoi_id': d_aoi_ids,
                'topic_id': d_topic_id
            }
        }


class AutoControlGuideQuestionLine(models.Model):
    _name = 'syap.ic.guide.question.line'
    _description = 'no description'
    _order = 'sequence asc'

    question_id = fields.Many2one('syap.ic.guide.question', 'Question', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=0, required=True)
    name = fields.Text('Title', required=False)
    code = fields.Char('Code', required=True, default=lambda self: uuid4().hex)
    response = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Response')
    response_explanation = fields.Many2many('syap.ic.question.explanation', string='Explanation')

    company_origin = fields.Char('Origin', help='Only for internal use')
    company_owner = fields.Char(related='question_id.guide_id.company_id.name',
                                store=True, help='Only for internal use')
