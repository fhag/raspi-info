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

__version__ = '0.0.13'


# def time_counter(timeout=5):
#     '''return time since start'''
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         yield max(time.time() - start_time, 0.01)

def time_counter():
    '''return time since start'''
    resp = 'reset'
    while resp != 'stop':
        if resp == 'reset':
            start_time = time.time()
        el_time = time.time() - start_time
        resp = yield round(el_time, 3)


def load_single_cpu(cpu_nr=0, timeout=6,
                    load_plan=[(3, 0.5), (4, 1.0)],
                    load_func=None):
    '''
    load CPI in intervalls
    - timeout = time to run load
    - load_plan changing load during runtime
      [(time_slice, loadpct)),]
    - load_func = function run for processor load
    '''
    def _load_func():
        '''Function to load cpu'''
        _ = math.log(random.random())
    if timeout == 0:
        return
    cpname = f'CPU[{cpu_nr:2.0f}] '
    _times, loads = zip(*load_plan)
    times_sum = sum(_times)
    times = [round(timeout * t / times_sum, 1) for t in _times]
    times = [sum(times[:i]) for i in range(1, len(times) + 1)]
    _load_plan = [(t, l) for t, l in zip(times, loads)]
    if load_func is None:
        load_func = _load_func
    start_functime = time.time()
    tcounter = time_counter()
    next(tcounter)
    runtime = -0.1
    ftext = f'{cpname} load started after {next(tcounter):.0f}' \
            f' seconds for {timeout:.0f} seconds'
    print(ftext)
    load_counter = time_counter()
    next(load_counter)
    while next(tcounter) < timeout:
        # print(f'1 {next(tcounter)} seconds')
        if next(tcounter) > runtime and _load_plan:
            runtime, loadpct = _load_plan.pop(0)
            ftext = f'{cpname} {loadpct:4.0%} load started' \
                    f' after {next(tcounter):4.0f} seconds'
            print(ftext)
            load_time = max(0, min(1, loadpct))
        load_counter.send('reset')
        # print(f'2 {next(tcounter)} seconds')
        while next(load_counter) < load_time:
            _ = load_func()
        # print(f'3 {next(tcounter)} seconds')
        while next(load_counter) < 1:
            sleep_time = abs(min(1 - next(load_counter), 1 - load_time))
            time.sleep(sleep_time)
            # print('sleep')
        # print(f'4 {next(tcounter)} seconds')
    try:
        tcounter.send('stop')
    except StopIteration:
        pass
    runtime = time.time() - start_functime
    ftext = f'{cpname} load terminated after {runtime:3.1f} seconds'
    return ftext


def sleep_until(seconds=1):
    '''sleep until full seconds'''
    time.sleep(max(0.1, seconds - time.time() % seconds))
    print(time.time())


def load_cpus(timeout=3, load_plan=[(1, 0.5)], max_cpus=None, delay=0):
    '''load cpu with defined percentage'''
    if delay > 0:
        print(f'Start CPU load delayed by {delay:.0f} seconds')
        time.sleep(delay)
        timeout = max(0, timeout - delay)
    if max_cpus is None or max_cpus > cpu_count():
        processes = cpu_count()
    else:
        processes = max_cpus
    func = partial(load_single_cpu, load_plan=load_plan, timeout=timeout)
    ftext = (f'Start test for {timeout:.0f} seconds '
             f'on {processes:.0f} CPUs '
             f'with initially {load_plan[0][1]:.0%} load')
    print(ftext)
    params = [i + 1 for i in range(processes)]
    stime = time.time()
    with Pool(processes=processes) as pool:
        _ = pool.map(func, params)
    print(f'Load CPUs terminated after {time.time()-stime:.2f} sec')


if __name__ == '__main__':
    TIMEOUT = 60
    LOAD_PLAN = [(1, 0.0), (1, 0.3), (1, 0.6), (1, 1.0)]
    MAX_CPUS = None
    DELAY = 1
    CONTEXT = dict(timeout=TIMEOUT,
                   load_plan=LOAD_PLAN,
                   max_cpus=MAX_CPUS,
                   delay=DELAY)
    THREADS = [Thread(target=load_cpus, kwargs=CONTEXT) for i in range(1)]
    _ = [t.start() for t in THREADS]
    _ = [t.join() for t in THREADS]
    print('finish')
