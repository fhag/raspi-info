# -*- coding: utf-8 -*-
'''
Start Main Routine for Raspberry Check
'''
__version__ = '0.0.2'

from raspicheck import RaspiCheck
import platform
import argparse

rel1, rel2, rel3 = platform.python_version_tuple()
if int(rel1) < 3 or int(rel2) < 7:
    raise('requires at least python 3.7')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Monitor CPU parameters with changing CPU load')
    parser.add_argument('setup', nargs='*', default= [''],
                        help='a string describing test setup')
    parser.add_argument('-t', '--timeout', type=int, 
                        default=600, metavar='', 
                        help='runtime of tests - timeout in seconds')
    args = parser.parse_args()
    setup = ' '.join(args.setup)
    timeout = args.timeout
    r = RaspiCheck(setup, timeout)
    r.main()
