# -*- coding: utf-8 -*-
'''
Start Main Routine for Raspberry Check

@author: GFI
requires Python 3.6 or later
'''
import argparse
import platform
from raspicheck import RaspiCheck

__version__ = '0.0.4'


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
    rcheck = RaspiCheck(setup, timeout)
    rcheck.main()
