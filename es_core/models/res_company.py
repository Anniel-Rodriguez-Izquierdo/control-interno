# -*- coding: utf-8 -*-

from uuid import uuid4

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    def _default_token(self):
        return uuid4().hex

    city = fields.Many2one(
        'res.country.state.city',
        string='City',
        ondelete='restrict',
        domain="[('state_id', '=?', state_id)]")
    company_registry = fields.Char(
        string="REEUP",
        index=True)
    vat = fields.Char(
        related='partner_id.vat',
        string="NIT",
        readonly=False)
    nae = fields.Char(
        related='partner_id.nae',
        string='NAE',
        readonly=False)
    activity = fields.Selection(
        selection=[('autofinanciado', 'Autofinanciado (empresas, uniones, grupos empresariales, etc)'),
                   ('presupuestadas', 'presupuestadas'),
                   ('oee_autofinanciado', 'OEE concebida que cubre sus gastos con sus ingresos (autofinanciada)'),
                   ('oee_presupuestada', 'OEE que cubren  parte de sus gastos con sus ingresos (presupuestada)'),
                   ('other', 'Otras')], string='Financing Form', required=True)
    company_type = fields.Selection(
        selection=[('ARCH', 'Archivo'),
                   ('AS', 'Asociación'),
                   ('BANC', 'Banco'),
                   ('BUFE', 'Bufete Colectivo'),
                   ('CAPE', 'Capital totalmente extranjero'),
                   ('CDR', 'Comité Defensa de La Revolución'),
                   ('CIRP', 'Carnet de Identidad Registro de Población'),
                   ('CONS', 'Consultoría'),
                   ('CT', 'Código de Trabajo'),
                   ('EMP', 'Empresa'),
                   ('GRUP', 'Grupo Empresarial'),
                   ('HOSP', 'Hospital'),
                   ('JUST', 'Justicia'),
                   ('MATE', 'Materno'),
                   ('MERC', 'Mercantil'),
                   ('MIXT', 'Mixta'),
                   ('NOTA', 'Notaria'),
                   ('OEE', 'Organización Económica Estatal'),
                   ('OPM', 'Organizaciones Políticas y de Masas'),
                   ('PMAT', 'Palacio de Matrimonios'),
                   ('POLI', 'Policlínicos'),
                   ('RCIV', 'Registro Civil'),
                   ('SOCC', 'Sociedad Civil'),
                   ('TRIB', 'Tribunales'),
                   ('U', 'Unión'),
                   ('UB', 'Unidad Básica'),
                   ('UNI', 'Unión'),
                   ('UP', 'Unidad Presupuestada'),
                   ('HOT', 'Hoteles'),
                   ('CNoA', 'Cooperativas No Agropecuarias'),
                   ('OTRO', 'Otro')], string='Company Type', required=True)
    token = fields.Char('Token',
                        default=_default_token)
    sql_provider_ids = fields.One2many('es.sql.provider', 'company_id', string='SQL Providers')

    # -----------------------------------------------------
    # Computes
    # -----------------------------------------------------
    @api.onchange('state_id')
    def _onchange_state(self):
        res = {'domain': {'city': []}}
        if self.state_id and self.state_id != self.city.state_id:
            self.city = False
            self.country_id = self.state_id.country_id
            res['domain']['city'] = [('state_id', '=', self.state_id.id)]
        return res

    @api.onchange('city')
    def _onchange_city(self):
        self.state_id = self.city.state_id
        if self.city.zip:
            self.zip = self.city.zip
