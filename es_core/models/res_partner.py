# -*- coding: utf-8 -*-

from odoo import api, models, fields

from .. import scripts


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_address_clean = fields.Char(compute='_compute_contact_address_clean', string='Complete Clean Address')
    country_id = fields.Many2one(default=lambda self: self.env.ref("base.cu"))
    city = fields.Many2one('res.country.state.city', string='City', ondelete='restrict',
                           domain="[('state_id', '=?', state_id)]")
    vat = fields.Char(
        string='NIT',
        help="The TAX Identification Number. Complete it if the contact is subjected to government taxes. "
             "Used in some legal statements.")
    nae = fields.Char(
        string='NAE')

    # -----------------------------------------------------
    # Computes
    # -----------------------------------------------------
    @api.multi
    def _compute_contact_address_clean(self):
        for record in self:
            if record.contact_address:
                record.contact_address_clean = record.contact_address.replace('\n', ', ')

    def _onchange_state(self):
        # aqui se esta redefiniendo el metodo original
        super(ResPartner, self)._onchange_state()
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

    # -----------------------------------------------------
    # Override
    # -----------------------------------------------------
    @api.model
    def _get_default_address_format(self):
        return scripts.CUBAN_FORMAT_ADDRESS

    @api.model
    def _get_address_format(self):
        return scripts.CUBAN_FORMAT_ADDRESS

    # -----------------------------------------------------
    # ORM
    # -----------------------------------------------------
    @api.model
    def create(self, vals):
        if 'name' in vals:
            if vals.get('type', False) == 'private':
                if not vals['name'].endswith(scripts.DEFAULT_PRIVATE_ADDRESS_LABEL):
                    vals['name'] = '%s - %s' % (vals['name'], scripts.DEFAULT_PRIVATE_ADDRESS_LABEL)

        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)

        for record in self:
            # para evitar que si se crea un PARTNER para representar DIRECCIONES no salgan como otra cosa en las vistas
            if record.type != 'contact':
                record.customer = False
                record.supplier = False
                record.employee = False
                record.is_company = False

        return res
