# -*- coding: utf-8 -*-
"""
Start Main Routine for Raspberry Check

@author: Gérard Fischer, CH-5103 Wildegg

only tested with Python 3.7 or later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""
import argparse
import platform
from raspicheck import RaspiCheck
try:
    from raspianalyse import plot_pdf
    PDF = True
except ImportError:
    PDF = False

__version__ = '0.1.5'

PATH = 'data/'

pversion = platform.python_version().replace('.', '')
if int(pversion) < 7:
    raise ValueError('requires at least python 3.7')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Monitor CPU parameters with changing CPU load')
    parser.add_argument('setup', nargs='*', default=[''],
                        help='a string describing test setup')
    parser.add_argument('-t', '--timeout', type=int,
                        default=600, metavar='',
                        help='runtime of tests - timeout in seconds')
    args = parser.parse_args()
    setup = ' '.join(args.setup)
    timeout = args.timeout
    rcheck = RaspiCheck(setup, timeout, path=PATH)
    ffname = rcheck.main()
    if PDF:
        plot_pdf(ffname)
