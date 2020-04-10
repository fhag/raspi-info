# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 13:31:33 2020

@author: GFI
requires Python 3.6 or later
"""
import math
import time
import random
from multiprocessing import Pool, cpu_count
from functools import partial
from threading import Thread

__version__ = '0.0.9'


def load_single_cpu(timeout=5, loadpct=1.00, load_func=None, fname=''):
    '''load cpu in intervalls'''
    def _load_func():
        '''Function to load cpu'''
        _ = math.log(random.random())

    if fname != '':
        ftext = f'CPU {loadpct:.0%} load ' \
                f'started for {timeout:.0f} seconds'
        with open(fname, 'a') as file:
            file.writeln(ftext)
    if load_func is None:
        load_func = _load_func
    load_time = max(0, min(1, loadpct))
    noload_time = 1 - load_time
    start_functime = time.time()
    while time.time() - timeout < start_functime:
        start_load = time.time()
        while time.time() < start_load + load_time:
            _ = load_func()
        start_noload = time.time()
        while time.time() < start_noload + noload_time:
            sleep_time = abs(min(start_noload + noload_time - time.time(),
                                 noload_time))
            time.sleep(sleep_time)
    runtime = time.time() - start_functime
    ftext = f'CPU load terminated after {runtime:3.1f} seconds'
    return ftext


def sleep_until(seconds=1):
    '''sleep until full seconds'''
    time.sleep(max(0.1, seconds - time.time() % seconds))
    print(time.time())


def load_cpus(timeout=3, loadpct=0.5, max_cpus=None, delay=0):
    '''load cpu with defined percentage'''
    if delay > 0:
        print(f'Start CPU load delayed by {delay:.0f} seconds')
        time.sleep(delay)
    if max_cpus is None or max_cpus > cpu_count():
        processes = cpu_count()
    else:
        processes = max_cpus
    func = partial(load_single_cpu, loadpct=loadpct)
    ftext = (f'Start test for {timeout:.0f} seconds '
             f'on {processes:.0f} CPUs '
             f'with {loadpct:.0%} load')
    print(ftext)
    params = [timeout, ] * processes
    stime = time.time()
    with Pool(processes=processes) as pool:
        _ = pool.map(func, params)
    print(f'Load CPUs terminated after {time.time()-stime:.2f} sec')


if __name__ == '__main__':
    TIMEOUT = 5
    LOADPCT = 0.6
    MAX_CPUS = 2
    DELAY = 0
    CONTEXT = dict(timeout=TIMEOUT, loadpct=LOADPCT,
                   max_cpus=MAX_CPUS, delay=DELAY)
    THREADS = [Thread(target=load_cpus, kwargs=CONTEXT) for i in range(2)]
    _ = [t.start() for t in THREADS]
    _ = [t.join() for t in THREADS]
    print('finish')
