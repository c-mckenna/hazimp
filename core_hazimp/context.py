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

#W0221: 65:ConfigAwarePipeLine.run: Arguments number differs from
# overridden method
# pylint: disable=W0221
# I'm ok with .run having more arg's
# I should use the ABC though.

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

import numpy
import csv

from core_hazimp import misc
from core_hazimp import parallel

# The standard string names in the context instance
EX_LAT = 'exposure_latitude'
EX_LONG = 'exposure_longitude'


class Context(object):
    """
    Context is a singlton storing all
    of the run specific data.
    """

    def __init__(self):
        # --------------  These variables are saved ----
        #  If new variables are added the save functions
        # will need to be modified.

        # Latitude and longitude values of the exposure data
        self.exposure_lat = None
        self.exposure_long = None

        # Data with a site dimension
        # key - data name
        # value - A numpy array. First dimension is site. (0 axis)
        self.exposure_att = {}
        # USE ONLY THIS DICTIONARY FOR DATA WITH A SITE DIMENSION
        # --------------  The above variables are saved ----

        # for example 'vulnerability_functions' is a list of a list of
        # vulnerabilty functions.  The outer list is for each asset.

        # A dictionary of the vulnerability sets.
        # Not associated with exposures.
        # key - vulnerability set ID
        # value - vulnerability set instance
        self.vulnerability_sets = {}

        # A dictionary with keys being vulnerability_set_ids and
        # value being the exposure attribute who's values are vulnerability
        # function ID's.
        self.vul_function_titles = {}

        # A dictionary of realised vulnerability curves, associated with the
        # exposure data.
        # key - intensity measure
        # value - realised vulnerability curves, only dimension is site.
        self.exposure_vuln_curves = None

    def save_exposure_atts(self, filename, use_parallel=True):
        """
        Save the exposure attributes, including latitude and longitude.
        The file type saved is based on the filename extension.
        Options
           '.npz': Save the arrays into a single file in uncompressed .npz
                   format.

        :param use_parallel: Set to True for parallel behaviour
        Which is only node 0 writing to file.
        :param filename: The file to be written.
        :return write_dict: The whole dictionary, returned for testing.
        """
        write_dict = self.exposure_att.copy()
        write_dict[EX_LAT] = self.exposure_lat
        write_dict[EX_LONG] = self.exposure_long

        if use_parallel:
            assert misc.INTID in write_dict
            write_dict = parallel.gather_dict(write_dict,
                                              write_dict[misc.INTID])

        if parallel.STATE.rank == 0 or not use_parallel:
            if filename[-4:] == '.csv':
                save_csv(write_dict, filename)
            else:
                numpy.savez(filename, **write_dict)
            # The write_dict is returned for testing
            # When running in paralled this is a way of getting all
            # of the context info
            return write_dict


def save_csv(write_dict, filename):
    """
    Save a dictionary of arrays as a csv file.
    the first dimension in the arrays is assumed to have the save length
    for all arrays.
    In the csv file the keys become titles and the arrays become values.

    If the array is higher than 1d the other dimensions are averaged to get a
    1d array.

    :param  write_dict: Write as a csv file.
    :type write_dict: Dictionary.
    :param filename: The csv file will be written here.
    """
    keys = write_dict.keys()
    header = list(keys)

    #  Lat, long ordering for the header
    header.remove(EX_LAT)
    header.remove(EX_LONG)
    header.insert(0, EX_LAT)
    header.insert(1, EX_LONG)

    body = None
    for key in header:
        #  Only one dimension can be saved.
        #  Average the results to the Site (first) dimension.
        only_1d = misc.squash_narray(write_dict[key])
        if body is None:
            body = only_1d
        else:
            body = numpy.column_stack((body, only_1d))

    # Need numpy 1.7 > to do headers
    #numpy.savetxt(filename, body, delimiter=',', header='yeah')
    hnd = open(filename, 'wb')
    writer = csv.writer(hnd, delimiter=',')
    writer.writerow(header)
    for i in range(body.shape[0]):
        writer.writerow(list(body[i, :]))