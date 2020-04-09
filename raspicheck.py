# -*- coding: utf-8 -*-

import subprocess
import string
from psutil import time, cpu_freq, cpu_percent
import unicodedata
from threading import Thread
from raspiload import load_cpus

__version__ = '0.0.14'


class RaspiCheck():
    '''Check CPU under different load parameter'''
    # define CPU test log parameters
    check_context = dict(setup='not defined',
                         timeout=600,
                         sleeptime=1)
    # define CPU load paramaters
    load_context = dict(timeout=check_context['timeout'] / 2,
                        loadpct=1,
                        max_cpus=None,
                        delay=check_context['timeout'] / 2)
    path = 'data/'

    def __init__(self, setup='', timeout=600):
        '''Initialise Raspi'''
        self.fname = self.valid_filename()
        self.load_cpus = load_cpus
        self.setup = setup
        self.timeout = timeout

    def valid_filename(self, txt='', path=None):
        '''Return valid filename with date'''
        if path is None:
            path = self.path
        validChars = "-_. %s%s" % (string.ascii_letters, string.digits)
        cleaned_txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore')
        cleaned_txt = cleaned_txt.decode('utf8').replace(' ', '_')
        cleaned_txt = ''.join(c for c in cleaned_txt if c in validChars)
        fname = f'rsp_{time.time():}'
        fname = f"{path}cr{time.strftime('%Y-%m-%d-%H%M%S')}_{cleaned_txt}.txt"
        return fname


    def raspi_check(self, setup='', timeout=3, sleeptime=1, log_all=False):
        '''Check raspi behaviour under load'''
        with open(self.fname, 'a') as file:
            file.write(self.fname + '\n')
            file.write(setup + '\n')
        cmds = [('vcgencmd get_throttled', 'CPU: {:>3s}', 'throttle0',
                 lambda x: ('NOK' if int(x, base=16) & 0b111 else 'ok')),
                ('vcgencmd get_throttled', 'Voltage: {:>3s}', 'throttle1',
                 lambda x: ('low' if int(x, base=16) & 0b1 else 'ok')),
                ('vcgencmd get_throttled', 'arm freq: {:>6s}', 'throttle2',
                 lambda x: ('capped' if int(x, base=16) & 0b10 else 'ok')),
                ('vcgencmd get_throttled', 'throttled: {:>3s}', 'throttle3',
                 lambda x: ('yes' if int(x, base=16) & 0b1 else 'no')),
                ('vcgencmd get_throttled', 'Soft temp limit: {:>8s}', 'throttle4',
                 lambda x: ('active' if int(x, base=16) & 0b1000 else 'inactive')),
                 ('vcgencmd measure_temp', 'Temp: {:>7s}', 'temp', 
                 lambda x: x.replace("'", "°")),
                ('vcgencmd measure_volts core', 'Volt: {:>9s}', 'volt', str),
                ('vcgencmd measure_clock arm', 'Freq: {:3,.2f}GHz', 'freq',
                 lambda x: int(x) / 1000000000),
                ]
        cmds_ps = [('cpu_freq().current', 'Freq:{:5,.2f}GHz', 'freq',
                    lambda x: x / 1000),
                   ('cpu_percent()', 'Load:{:4.0%} ', 'load',
                    lambda x: x / 100),
                   ('cpu_percent(percpu=True)', '[{}]', 'percpu',
                    lambda x: ', '.join([f'{i/100:4.0%}' for i in
                                         sorted(x, reverse=True)])),
                   ]
        stime = time.time()
        counter = 0
        while (time.time() - stime) < timeout:
            intro = f'Core data - After {time.time() - stime:5.1f} seconds'
            res_dict = dict(intro=intro)
            for cmdline, fstr, key, func in cmds:
                cmd = cmdline.split()
                try:
                    res = subprocess.run(cmd, capture_output=True,
                                         timeout=1, check=True)
                    res_txt = res.stdout.decode()
                    _, res_data = res_txt.split('=')
                    # print(fstr.format(func(res_data)))
                    res_dict[key] = fstr.format(func(res_data)).strip()
                except FileNotFoundError:
                    print('no raspi')
            for cmdline, fstr, key, func in cmds_ps:
                res = eval(cmdline)
                res = fstr.format(func(res))
                res_dict[key] = res
            result = ' | '.join(res_dict.values())
            if (res_dict['throttle0'][-2:] != 'ok') or (counter % 10 == 0) or log_all:
                print(f'{counter:4.0f}. {result}')
                with open(self.fname, 'a') as file:
                    file.write(result + '\n')
            counter += 1
            time.sleep(sleeptime)
        print(f'Check results in file: {self.fname}')

    def main(self):
        if self.setup == '':
            self.setup = input('Enter test setup:')          
        check_context = self.check_context.copy()
        check_context['setup'] = self.setup
        check_context['timeout'] = self.timeout
        load_context = self.load_context.copy()
        load_context['timeout'] = int(self.timeout / 2)
        load_context['delay'] = int(self.timeout / 2)       
        start_time = time.time()
        runtxt = f'{self.setup!r} running for ' \
                 f'{check_context["timeout"]/60:4.1f} minutes'
        print(runtxt)
        self.fname = self.valid_filename(self.setup)
        threads = [Thread(target=self.load_cpus, kwargs=load_context),
                    Thread(target=self.raspi_check,
                    kwargs=check_context)]

        [t.start() for t in threads]
        [t.join() for t in threads]
        print(f'Finished after {time.time() - start_time:.0f} seconds')



if __name__ == '__main__':
    pass
