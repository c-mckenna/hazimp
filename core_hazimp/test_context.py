# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Geoscience Australia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the workflow module.
"""

import numpy
import unittest
import tempfile
import os

from scipy import allclose, array

from core_hazimp import context
from core_hazimp import misc


class TestContext(unittest.TestCase):
    """
    Test the workflow module
    """

    def test_save_exposure_atts(self):

        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.npz',
                                        prefix='test_save_exposure_atts',
                                        delete=False)
        f.close()

        con = context.Context()
        actual = {'shoes': array([10., 11]),
                  'depth': array([[5., 3.], [2., 4]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 2.])
        con.exposure_lat = lat
        lon = array([10., 20.])
        con.exposure_long = lon
        con.save_exposure_atts(f.name, use_parallel=False)
        exp_dict = numpy.load(f.name)

        actual[context.EX_LONG] = lon
        actual[context.EX_LAT] = lat
        for keyish in exp_dict.files:
            self.assertTrue(allclose(exp_dict[keyish],
                                     actual[keyish]))
        os.remove(f.name)

    def test_save_exposure_attsII(self):

        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.csv',
                                        prefix='test_save_exposure_atts',
                                        delete=False)
        f.close()
        con = context.Context()
        actual = {'shoes': array([10., 11, 12]),
                  'depth': array([[5., 4., 3.], [3., 2, 1], [30., 20, 10]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 2., 3])
        con.exposure_lat = lat
        lon = array([10., 20., 30])
        con.exposure_long = lon
        con.save_exposure_atts(f.name, use_parallel=False)
        exp_dict = misc.csv2dict(f.name)

        actual[context.EX_LONG] = lon
        actual[context.EX_LAT] = lat
        actual['depth'] = array([4, 2, 20])
        for key in exp_dict:
            self.assertTrue(allclose(exp_dict[key],
                                     actual[key]))
        os.remove(f.name)


#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestContext, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)