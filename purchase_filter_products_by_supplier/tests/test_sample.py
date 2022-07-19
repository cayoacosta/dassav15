# -*- coding: utf-8 -*-

import logging

from openerp import fields

import openerp
import openerp.tests

from openerp.tests import common
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)
_testall = True


@openerp.tests.common.at_install(_testall)
@openerp.tests.common.post_install(False)
class TestSample(common.TransactionCase):
    def setUp(self):
        super(TestSample, self).setUp()

    def test_001_sample_one(self):
        self.assertEqual('1', '1')
