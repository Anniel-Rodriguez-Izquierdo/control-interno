# -*- coding: utf-8 -*-

import logging
import os

from lxml import etree

from odoo.loglevels import ustr
from odoo.tools import misc, view_validation

_logger = logging.getLogger(__name__)

_dashboard_validator = None
_cohort_validator = None


@view_validation.validate('dashboard')
def schema_dashboard(arch):
    # Check the dashboard view against its schema
    # :type arch: etree._Element
    global _dashboard_validator

    if _dashboard_validator is None:
        with misc.file_open(os.path.join('es_core', 'static', 'rng', 'dashboard.rng')) as f:
            _dashboard_validator = etree.RelaxNG(etree.parse(f))

    if _dashboard_validator.validate(arch):
        return True

    for error in _dashboard_validator.error_log:
        _logger.error(ustr(error))

    return False


@view_validation.validate('cohort')
def schema_cohort(arch):
    # Check the cohort view against its schema
    # :type arch: etree._Element
    global _cohort_validator

    if _cohort_validator is None:
        with misc.file_open(os.path.join('es_core', 'static', 'rng', 'cohort.rng')) as f:
            _cohort_validator = etree.RelaxNG(etree.parse(f))

    if _cohort_validator.validate(arch):
        return True

    for error in _cohort_validator.error_log:
        _logger.error(ustr(error))
    return False
