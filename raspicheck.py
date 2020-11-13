# -*- coding: utf-8 -*-
"""
Check Raspberry CPU over timeout (in seconds)

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
import subprocess
import string
import unicodedata
from threading import Thread
from queue import Queue
from functools import lru_cache
import psutil
from psutil import time
# from subprocess import SubprocessError
from raspiload import load_cpus

__version__ = '0.1.13'


class RaspiCheck():
    '''Check CPU under different load parameter'''
    # define default context for raspicheck
    raspicheck_context = dict(setup='',
                              timeout=600,
                              sleeptime=1)
    # define default context for raspiload
    raspiload_context = dict(timeout=raspicheck_context['timeout'],
                             load_plan=[(1, 0.1), (1, 0.3),
                                        (1, 0.6), (1, 1.0)],
                             max_cpus=None,
                             delay=10)

    def __init__(self, setup='', timeout=600, delay=0, path='data/'):
        '''Initialise Raspi'''
        self.path = path
        self.load_cpus = load_cpus
        self.setup = setup
        self.timeout = float(timeout)
        self.delay = float(delay)
        self.tcounter = self.time_counter()
        self.queue = Queue()

    @staticmethod
    def time_counter():
        '''return time since start'''
        resp = 'reset'
        while resp != 'stop':
            if resp == 'reset':
                start_time = time.time()
            el_time = time.time() - start_time
            resp = yield round(el_time, 2)

    @staticmethod
    @lru_cache(maxsize=1)
    def is_raspbian():
        '''check if Raspian Linux installed'''
        try:
            fnames = psutil.os.listdir('/etc')
        except FileNotFoundError:
            return False
        else:
            fnames = [f for f in fnames if f.endswith('-release')]
            for fname in fnames:
                with open('/etc/' + fname, 'r') as file:
                    data = file.read()
                if 'raspbian' in data.lower():
                    return True
        return False

    @lru_cache(maxsize=1)
    def valid_filename(self, txt='', path=None):
        '''Return valid filename with date'''
        if path is None:
            path = self.path
        valid_chars = "-_. %s%s" % (string.ascii_letters, string.digits)
        cleaned_txt = unicodedata.normalize('NFKD', txt).encode('ASCII',
                                                                'ignore')
        cleaned_txt = cleaned_txt.decode('utf8').replace(' ', '_')
        cleaned_txt = ''.join(c for c in cleaned_txt if c in valid_chars)
        fname = f'rsp_{psutil.time.time():}'
        dtime = psutil.time.strftime('%Y-%m-%d-%H%M%S')
        fname = f"{path}cr{dtime}_{cleaned_txt}.txt"
        return fname

    def run_vcgencmd(self, cmd):
        '''Return answer from subprocess'''
        fullcmd = f'vcgencmd {cmd}'
        try:
            assert self.is_raspbian()
            res = subprocess.run(fullcmd, capture_output=True,
                                 timeout=0.3, check=True, shell=True)
            res_txt = res.stdout.decode()
            assert 'error' not in res_txt
        except (AssertionError, subprocess.CalledProcessError):
            okay, res_data = False, ' - '
        else:
            okay, (_, res_data) = True, res_txt.split('=')
        return okay, res_data.strip()

    def get_throttled(self) -> str:
        '''Get throttled digit if available'''
        okay, res = self.run_vcgencmd('get_throttled')
        if okay:
            states = list()
            throttled = int(res, 0)
            if throttled & 0b111:
                states = ['CPU: NOK']
            else:
                states = ['CPU:  ok']
            if throttled & 0b1:
                states.append('Voltage: low')
            else:
                states.append('Voltage:  ok')
            if throttled & 0b10:
                states.append('arm freq: capped')
            else:
                states.append('arm freq:  ok   ')
            if throttled & 0b100:
                states.append('throttled: yes')
            else:
                states.append('throttled:  no')
            return states
        return [f'CPU: data not available']

    @staticmethod
    def get_temperature() -> str:
        '''Get temperature'''
        res = getattr(psutil, 'sensors_temperatures', '   - °C')
        try:
            result = res()['cpu_thermal'][0]
            res = f'Temp: {result.current:5.1f}°C'
        except TypeError:
            res = 'Temp:    - °C'
        return res

    def get_voltage(self) -> str:
        '''Get CPU voltage'''
        okay, res = self.run_vcgencmd('measure_volts core')
        if okay:
            voltage = float(res[:-1])
            return f'Volt: {voltage:>6.4f}V'
        return f'    - V'

    @staticmethod
    def get_frequency() -> str:
        '''Get CPU frequency'''
        return f'Freq:{psutil.cpu_freq().current / 1000:5,.2f}GHz'

    @staticmethod
    def get_cpu_avg_load() -> str:
        '''Get average CPU load'''
        return f'Load:{psutil.cpu_percent(percpu=False):4.0f}% '

    @staticmethod
    def get_cpu_all_load() -> str:
        '''Get load of all CPUs'''
        freqs = psutil.cpu_percent(percpu=True)
        if freqs:
            freqs = [f'{f:3.0f}%' for f in freqs]
        else:
            freq = f'{psutil.cpu_percent(percpu=False):3.0f}%'
            freqs = [freq, ] * psutil.cpu_count()
        freqs = f'[{",".join(freqs)}]'
        return freqs

    def raspi_check(self, setup='', timeout=None,
                    sleeptime=1, log_all=False):
        '''Check raspi behaviour under load'''
        if not setup:
            setup = self.setup
        if timeout is None:
            timeout = self.timeout
        lines = [self.valid_filename(setup), setup]
        next(self.tcounter)
        self.tcounter.send('reset')
        counter = 0
        stepper = min(10, max(1, round(timeout / 10, 0)))
        if log_all:
            stepper = 1
        while next(self.tcounter) < timeout:
            line_list = [f'Core data - After {next(self.tcounter):5.1f}'
                         f' seconds']
            line_list.extend(self.get_throttled())
            line_list.append(self.get_temperature())
            line_list.append(self.get_voltage())
            line_list.append(self.get_frequency())
            line_list.append(self.get_cpu_avg_load())
            line_list.append(self.get_cpu_all_load())
            line = ' | '.join(line_list)
            counter += 1
            if 'NOK' in line or (counter % stepper == 0):
                print(f'{counter:4.0f}. {line}')
                lines.append(line)
            time.sleep(sleeptime - time.time() % sleeptime)
        filetxt = '\n'.join(lines)
        self.queue.put(filetxt)

    def main(self):
        '''Start CPU check'''
        if self.setup == '':
            self.setup = input('Enter test setup:')
        raspicheck_context = self.raspicheck_context.copy()
        raspicheck_context['setup'] = self.setup
        raspicheck_context['timeout'] = self.timeout
        raspicheck_context['log_all'] = False
        # start raspiload with 50% load after 1/3 of total timeout
        raspiload_context = self.raspiload_context.copy()
        raspiload_context['load_plan'] = [(1, 0.1), (1, 0.3),
                                          (1, 0.6), (1, 1.0)]
        raspiload_context['timeout'] = self.timeout
        raspiload_context['delay'] = self.delay

        start_time = time.time()
        runtxt = f'{self.setup!r} running for ' \
                 f'{raspicheck_context["timeout"]/60:4.1f} minutes'
        print(runtxt)
        threads = [Thread(target=self.load_cpus, kwargs=raspiload_context)]
        threads.append(
            Thread(target=self.raspi_check, kwargs=raspicheck_context))
        _ = [t.start() for t in threads]
        self.threads = threads
        _ = [t.join() for t in threads]
        print(', '.join(
            [f"{t.name} {'stopped' if t._is_stopped else 'running'}"
             for t in threads]))
        filetxt = self.queue.get()
        fname = self.valid_filename(self.setup)
        with open(fname, 'a', encoding='utf8') as file:
            file.write(filetxt)
        print(f'Check results in file: {self.valid_filename(self.setup)}')
        print(f'Finished after {time.time() - start_time:.0f} seconds')
        return fname


if __name__ == '__main__':
    rc = RaspiCheck(setup='test')
    rc.raspi_check(timeout=5, setup='Raspi test')
    # print(rc.run_vcgencmd('test'))
    # print(rc.get_cpu_all_load())
    # print(rc.get_cpu_avg_load())
    # print(rc.get_temperature())
    # print(rc.get_frequency())
    # print(rc.get_throttled())
    # print(rc.get_voltage())
