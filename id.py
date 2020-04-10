# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 06:17:18 2020

@author: GFI

requires Python 3.6 or later
"""
import sys
import socket
import time
from platform import uname
from os import popen
import psutil

__version__ = '0.1.5'


# Raspi 4 shows BCM2835 instead of BCM2711
RASPIS = [
    {'Raspberry Pi 4 Model B 1GB': ['BCM2835', '1500', '1024']},
    {'Raspberry Pi 4 Model B 2GB': ['BCM2835', '1500', '2048']},
    {'Raspberry Pi 4 Model B 4GB': ['BCM2835', '1500', '4096']},
    {'Raspberry Pi 3 Model B+': ['1400', '1024']},
    {'Raspberry Pi 3 Model A+': ['1400', '512']},
    {'Raspberry Pi 3 Model B': ['1200', '1024']},
    {'Raspberry Pi 2 Model B': ['900', '1024']},
    {'Raspberry Pi Zero W': ['BCM2835', '1000', '1024']},
    {'Raspberry Pi Zero': ['BCM2835', '1000', '1024']},
    {'Raspberry Pi 1 Model B+': ['BCM2835', '700', ]},
    {'Raspberry Pi 1 Model A+': ['BCM2835', '700', ]},
    ]


def raspi_model():
    '''Return Raspi Model'''
    global RASPIS
    cpu_dict = get_cpudict()
    if cpu_dict:
        tot_mem = str(_get_mem())
        proc = cpu_dict['Hardware']
        cpu_freq = f'{psutil.cpu_freq().current:.0f}'
        criterias = [cpu_freq, proc, tot_mem]
        for raspi in RASPIS:
            values = list(raspi.values())[0]
            res = [v in criterias for v in values]
            if all(res):
                return list(raspi.keys())[0] + '\n'
    return 'kein Raspberry PI\n'


def pi_camera():
    '''Detect Pi Camera Modul'''
    try:
        with open('/boot/config.txt', 'r') as file:
            config = file.readlines()
        assert 'start_x' in ''.join(config)
    except (AssertionError, FileNotFoundError):
        return ''
    else:
        camtypes = {'ov5647': 'v1 Omnivision OV5647-5MP 2592 x 1944 Px',
                    'imx219': 'v2 Sony IMX219 8MP 3280 x 2464 Px'}
        try:
            import picamera
        except ModuleNotFoundError:
            return ''
        try:
            with picamera.PiCamera() as cam:
                camtype = cam.revision
        except picamera.exc.PiCameraError:
            return ''
        camtype = camtypes.get(camtype, '')
        if camtype:
            return f'Pi Camera Modul    : {camtype}\n'
        return ''


def pretty_size(nr_of_bytes) -> str:
    '''return string in KB, MB or GB'''
    extensions = ['GB', 'MB', 'KB', 'B']
    nrbytes = int(nr_of_bytes) / 1024 ** 3
    for extension in extensions:
        if nrbytes >= 1:
            return f'{nrbytes:.0f}{extension}'
        nrbytes = nrbytes * 1024
    return ''


def system_info():
    '''get system info'''
    pname = uname()
    infotxt = (f'System             : {pname.system}{pname.version}\n'
               f'Machine            : {pname.machine}\n'
               f'Processor          : {getattr(pname, "processor", "n/a")}\n'
               )
    return infotxt


def welcome() -> str:
    '''Welcome header'''
    hostname = socket.gethostname()
    return f'Welcome to {hostname!r}'


def python_version() -> str:
    '''Return python version information'''
    version = ' '.join(sys.version.split('\n'))
    version = 'Python version     : %s\n' % version
    vinfo = sys.version_info
    if vinfo.major * 10 + vinfo.minor >= 36:
        return version
    raise 'Invalid python version'


def debian_version() -> str:
    '''Returns Debian Version if running on linux'''
    with popen('cat /etc/debian_version') as file:
        line = file.readline()
    if line:
        return f'Platform           : {sys.platform} {line.strip()}\n'
    return f'Platform           : {sys.platform} {sys.winver}\n'


def disk_space() -> str:
    '''Return available disk space'''
    dsk = psutil.disk_usage('.')
    dskt = pretty_size(dsk.total)
    dskf = pretty_size(dsk.free)
    dskp = f'{dsk.percent:3.0f}%'
    return f'Disk Space         : total={dskt} used={dskp} free={dskf}\n'


def _get_mem():
    '''Return RAM in megabytes'''
    megabytes = 1048576
    gigabytes = megabytes * 1024
    with popen('vcgencmd get_mem arm') as file:
        line1 = file.readline()
    with popen('vcgencmd get_mem gpu') as file:
        line2 = file.readline()
    try:
        arm_mem = int(line1[4:-2]) * megabytes
        gpu_mem = int(line2[4:-2]) * megabytes
        virt_mem = psutil.virtual_memory().total
        if virt_mem > gigabytes:
            tot_mem = int(round((virt_mem + gpu_mem) / gigabytes,
                                0) * gigabytes)
        else:
            tot_mem = arm_mem + gpu_mem
    except ValueError:
        tot_mem = psutil.virtual_memory().total
    return int(tot_mem / megabytes)


def memory_info() -> str:
    '''Return formatted total memory'''
    megabytes = 1048576
    return f'Total memory       : {pretty_size(_get_mem() * megabytes)}\n'


def cpu_info() -> str:
    '''REturn CPU information'''
    cpu_log = psutil.cpu_count(logical=True)
    cpu_phy = psutil.cpu_count(logical=False)
    cpu_phy = '-' if cpu_phy is None else cpu_phy
    cpu_freq = psutil.cpu_freq().current
    infotxt = (f'# of CPUs          : {cpu_phy} [{cpu_log}]\n'
               f'CPU frequency      : {cpu_freq:,.0f}Mhz\n'
               )
    return infotxt


def os_release():
    '''Return os information if running on linux'''
    if 'linux' not in sys.platform:
        return ''
    info = dict()
    with popen('cat /etc/*-release') as file:
        for line in file:
            if '=' in line:
                key, value = line.split('=')
                info[key] = value.strip('"')
    infotxt = (f'Pretty Name        : {info["PRETTY_NAME"]}'
               f'Home URL           : {info["HOME_URL"]}'
               f'Support URL        : {info["SUPPORT_URL"]}'
               )
    return infotxt


def get_cpudict():
    '''Return Dict with CPU Information'''
    if 'linux' not in sys.platform:
        return ''
    infos = dict()
    with popen('cat /proc/cpuinfo') as file:
        for line in file:
            if ':' in line:
                key, value = [val.strip().strip('\t')
                              for val in line.split(':')]
                infos[key.strip('\t')] = value
    with popen('cat /etc/os-release') as file:
        for line in file:
            if '=' in line:
                key, value = line.split('=')
                infos[key] = value.strip('"')
    return infos


def all_cpuinfo():
    '''Return all key cpu info'''
    if 'linux' not in sys.platform:
        return f'{cpu_info()}'
    infos = get_cpudict()
    cpu_arch = infos.get("CPU architecture")
    cpu_rev = infos.get("CPU revision")
    info = (f'Model              : {infos.get("Model")}\n'
            f'Processorname      : {infos.get("model name")}'
            f' {cpu_arch}.{cpu_rev}\n'
            f'Hardware - Revision: {infos.get("Hardware")}'
            f' - {infos.get("Revision")}\n'
            f'{cpu_info()}'
            f'BogoMIPs/CPU       : {infos.get("BogoMIPS")}\n'
            f'CPU serial         : {infos.get("Serial")}\n'
            )
    return info


def net_info():
    '''return active connections information'''
    conns = psutil.net_if_stats()
    ifs = psutil.net_if_addrs()
    info_txts = ['Active Connections', ]
    for conn, snicstats in conns.items():
        if snicstats.isup:
            connifs = ifs[conn]
            for connif in connifs:
                if str(connif.family.name) == 'AF_INET':
                    ftext = f'- {conn[:17]:17s}: {connif.address}'
                    info_txts.append(ftext)
    return '\n'.join(info_txts) + '\n'


def net_active():
    '''True if internet available'''
    try:
        socket.gethostbyname('www.google.com')
        return True
    except Exception:
        return False


def get_allinfo():
    '''Return string with all computer info'''
    _ = python_version()
    num = 80
    id_version = f' id.py {__version__} -- {time.ctime()} '.center(num, '-')
    txt = (f' {welcome()} '.center(num, '-') + '\n'
           f'Computer Model     : {raspi_model()}'
           f'{memory_info()}'
           f'{disk_space()}'
           f'{all_cpuinfo()}'
           f'{system_info()}'
           f'{os_release()}'
           f'{debian_version()}'
           f'{python_version()}'
           f'{net_info()}'
           f'{pi_camera()}'
           f'{ id_version }\n'
           )
    return txt


def main():
    '''Show data only if internet connection established'''
    while not net_active():
        time.sleep(1)
    txt = get_allinfo()
    print(txt)
    with open('id.txt', 'w+') as file:
        for line in txt:
            file.write(line)


if __name__ == '__main__':
    main()
