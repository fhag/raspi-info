# -*- coding: utf-8 -*-
"""
Extracting values from log file and preparing chart


"""
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import numpy as np

__version__ = '0.0.5'

colfuncs = {'Core data': [re.compile(r'(?: \d{1,4}\.{1}\d{1} )'),
                          float,
                          'seconds',
                          (0, 1)],
            'Throttled': [re.compile(r'(?:0|1){19}'),
                          str,
                          'Throttled',
                          (0, 1)],
            'CPU:': [re.compile(r'(NOK|ok)'),
                     lambda x: 'NOK' in x,
                     'CPU not ok',
                     (0, 1)],
            'Voltage:': [re.compile(r'(ok|low)'),
                         lambda x: 'low' in x,
                         'Voltage not ok',
                         (0, 1)],
            'arm freq:': [re.compile(r'(capped|ok)'),
                          lambda x: 'capped' in x,
                          'arm freq capped',
                          (0, 1)],
            'throttled:': [re.compile(r'(yes|no)'),
                           lambda x: 'yes' in x,
                           'CPU throttled',
                           (0, 1)],
            'temp limit:': [re.compile(r'(active|inactive)'),
                            lambda x: 'inactive' in x,
                            'software temp limit',
                            (0, 1)],
            'Volt:': [re.compile(r'(?: \d\.{1}\d{3,4})'),
                      float,
                      'voltage',
                      (0, None)],
            'Temp': [re.compile(r'(?: \d{2,3}\.{1}\d{1})'),
                     float,
                     'temperature',
                     (0, None)],
            'Freq': [re.compile(r'(?: \d{1}\.{1}\d{2})'),
                     float,
                     'frequency in GHz',
                     (0, None)],
            'Load': [re.compile(r'(?:\d{1,3}%)'),
                     lambda x: float(x[:-1]),
                     'CPU load in %',
                     (0, 100)],
            '[': [re.compile(r'(?:\d{1,3}%)'),
                  lambda x: float(x[:-1]),
                  'test',
                  (0, 100)],
            }


def get_rawdata(fname, path=''):
    '''Return raw data'''
    try:
        with open(os.path.join(path, fname), 'r', encoding='utf8') as file:
            raw = file.read()
    except UnicodeDecodeError:
        with open(os.path.join(path, fname), 'r') as file:
            raw = file.read()
    return raw


def read_rawdata(rawdata):
    ''''''
    lines = rawdata.split('\n')
    title_fname = lines.pop(0)
    title = lines.pop(0)
    res_dict = defaultdict(list)
    for line in lines:
        cols = line.split(' | ')
        for col in cols:
            keylist = [key for key in colfuncs.keys() if key in col]
            if keylist:
                key = keylist[0]
                # print(key)
                regex, func, *_ = colfuncs[key]
                results = re.findall(regex, col)
                num = 'nores'
                for i, result in enumerate(results):
                    try:
                        num = func(result)
                    except ValueError:
                        print('na!!')
                        num = 'na'
                    colhead = key.replace(':', '').replace(' ', '_')
                    colhead = key
                    if '[' in colhead:
                        colhead = f'cpu{i}'
                    res_dict[colhead].append(num)

                    if num == 'naa' or num == 'nores':
                        print(f'key={key!r:10s} in {col!r} ={num} with '
                              f'{func} and re {re.findall(regex, col)}')
                    else:
                        # print(f'key={key!r:10s} in {col!r} ={num}')
                        pass
            else:
                print(line)
    return title, title_fname, dict(res_dict)


def add_textbox(ax, text):
    '''Add textbox to subplot'''
    ax.text(0.5, 0.5, text, fontsize=12, fontweight='bold',
            bbox=dict(facecolor='yellow', alpha=0.1,
                      edgecolor='red', linewidth=3,
                      boxstyle='round4', pad=.91),
            horizontalalignment='center',
            color='red', transform=ax.transAxes)
    return ax


def plot_pdf(fname, datapath='', chartpath=''):
    '''Create pdf and show charts'''
    print('Starting creating charts')
    A4portrait = (8.27, 11.69)
    rawdata = get_rawdata(fname, datapath)
    title, title_fname, data = read_rawdata(rawdata)
    # nrofsupplots = len(data.keys()) - 1
    xvalues = data['Core data']
    dummy = [np.nan] * len(xvalues)
    fig = plt.figure(figsize=A4portrait,
                     frameon=True)
    fig.suptitle(title, size=16, color='blue', fontweight='bold')
    gspec = fig.add_gridspec(nrows=5, ncols=2,
                             bottom=0.05, top=0.93,
                             left=0.1, right=0.95,
                             hspace=0.33, wspace=0.25)
    axes = list()
    # draw first data
    plotdata = [['Temp', '°C', 'Temperature', 'default',
                 (None, None), (0, 0)],
                ['Load', 'in %', 'CPU load', 'steps',
                 (0, 105), (1, 0)],
                ['Freq', 'GHz', 'CPU Frequency', 'steps',
                 (None, None), (4, 0)],
                ['Volt:', 'Voltage', 'CPU Voltage', 'steps',
                 (None, None), (4, 1)]]
    for y, label, title, ds, ylim, pos in plotdata:
        ax = fig.add_subplot(gspec[pos])
        ax.plot(xvalues, data.get(y, dummy), lw=3, drawstyle=ds)
        ax.set_ylim(ylim)
        ax.set_ylabel(label)
        ax.set_title(title)
        if y not in data.keys():
            ax = add_textbox(ax, f'no data for {title!r}')
            plt.yticks(visible=False)
        axes.append(ax)
    # draw digital data
    plotdata = [
        ['Voltage:', 'Under-voltage detected', (0, 1)],
        ['arm freq:', 'Arm frequency capped', (1, 1)],
        ['throttled:', 'CPU throttled', (2, 1)],
        ['throttled:', 'Soft temperate limit active', (3, 1)], ]
    for y, title, pos in plotdata:
        ax = fig.add_subplot(gspec[pos])
        ax.fill_between(xvalues, data.get(y, dummy),
                        step="mid", alpha=0.3, color='red')
        ax.set_title(title, loc='center')
        ax.set_ylim((0, 1))
        if y not in data.keys():
            ax = add_textbox(ax, f'no data for \n{title!r}')
        axes.append(ax)
        plt.yticks(visible=False)
    # draw cumulative cpu load
    ax = fig.add_subplot(gspec[2:4, 0])
    datas = [data[k] for k in data.keys() if k.startswith('cpu')]
    ax.stackplot(xvalues, *datas, alpha=.6)
    ax.set_title('all CPUs load', loc='center')
    ax.set_ylabel('cumulative CPU load in %')
    axes.append(ax)
    # set common parameters
    xlim = (0, max(xvalues))
    for ax in axes:
        ax.grid(True)
        ax.set_xlim(xlim)
        ax.set_title(ax.get_title(), fontweight='bold')
        ax.set_ylabel(ax.get_ylabel(), fontweight='bold', fontsize=11)
    pdf_fname = title_fname.replace('.txt', '.pdf')
    pdf_fname = pdf_fname.replace(datapath, chartpath)
    try:
        os.mkdir(chartpath)
    except (FileExistsError, FileNotFoundError):
        pass
    fig.savefig(pdf_fname)
    print('Charts save as pdf to: ', pdf_fname)
    return fig


if __name__ == '__main__':
    DATAPATH = 'data/'
    CHARTPATH = 'charts/'
    fnames = [fname for fname in os.listdir(DATAPATH)
              if fname.endswith('.txt')]
    fnames = [fname for fname in fnames if '05-02' in fname]
    for fname in fnames:
        try:
            print(fname)
            fig = plot_pdf(fname, datapath=DATAPATH, chartpath=CHARTPATH)
            plt.close()
        except KeyError:
            print('Error for :', fname)
    fig.show()
