<small id='version'>v0.0.9</small>
<!--
@author: GFI
FHAG
-->
<h1 id='raspiinfo' style='color:DodgerBlue'><b>raspi-info.py</b></h1>
Utilies to collect information about your Raspberry and
monitor CPU status under load.
This code was developped to check power supplies and cables of Raspberry Pi 3+,
as my Raspi lost sometimes the WiFi Connection or crashed without reason.
It turned out, that due to a bad power supply and cable the processor was
throttled.

The actual state can be read out with `vcgencmd get_throttled`. For testing
 different combinations of power supply and cables this code was used.

Learnings are:
- Do not rely on indications of power supply: 5v, 2.5A indications looks fine,
 but a poor power supply can slow down your Raspi.
- Strong power supply do not automatically provide the stable power
required by your Raspi.
- Try different cables in combination. Expensive cables are not the best.
- Under heavy CPU load a throttling of Raspi CPUs is happening more often


<h2 style='color:DodgerBlue'><b>Table of contents</b></h2>

1. <a href='#raspi'>raspi.py</a>
2. <a href='#raspicheck'>raspicheck.py</a>
3. <a href='#raspiload'>raspiload.py</a>
4. <a href='#id'>id.py</a>
5. <a href='#vpy'>v.py</a>
6. <a href='#showfonts'>showfonts.py</a>

<br>
<a href='#raspiinfo'>return to top</a>

---
---
<h2 id='raspi' style='color:DodgerBlue'><b>raspi.py</b></h2>

**Usage**

Run this code with different power supplies and cables to find weak
combinations. The printout and saved text shows if *under-voltage* is detected,
*Arm frequency* is capped, CPU is *throttled* or a "Soft temperature limit"
 is active. Testing during 10 minutes, whereas the last half is tested under
 heavy CPU load, shows failing cases.

The created file can be parsed for some statistical analysis the lines are fixed length.

**how to use**

- setup = Description of setup is added to file name and stored to textfile.
If empty the user is prompted to input setup information.
- timeout = number of seconds to apply checking.

bash command line
```console
$ python3 raspi.py -h
usage: raspi.py [-h] [-t] [setup [setup ...]]

Monitor CPU parameters with changing CPU load

optional arguments:
  setup            a string describing test setup
  -h, --help       show this help message and exit
  -t , --timeout   runtime of tests - timeout in seconds
```
If `setup` is an empty string (''), an input is requested after start.

```python
Enter test setup:
```

**Sample Output**

command line start

```console
$ python3 raspi.py sample-raspi -t 5
'sample-raspi' running for  0.1 minutes
Start CPU load delayed by 2 seconds
   0. Core data - After   0.0 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 44.0°C | Volt:  1.2000V | Freq: 1.40GHz | Load: 28%  | [ 71%,  21%,  15%,   4%]
   1. Core data - After   1.1 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 44.0°C | Volt:  1.2000V | Freq: 0.60GHz | Load:  4%  | [  5%,   4%,   4%,   3%]
Start test for 2 seconds on 4 CPUs with 100% load
   2. Core data - After   2.2 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 45.1°C | Volt:  1.2000V | Freq: 1.40GHz | Load: 43%  | [ 45%,  43%,  41%,  41%]
   3. Core data - After   3.7 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 45.1°C | Volt:  1.2000V | Freq: 1.40GHz | Load:100%  | [100%, 100%, 100%, 100%]
Load CPUs terminated after 2.19 sec
Check results in file: data/cr2020-04-10-094643_sample-raspi.txt
Finished after 5 seconds
```
... created the following text file:
```console
$ ls -l data/*sample*.txt
-rw-r--r-- 1 pi pi 899 Apr 10 09:46 data/cr2020-04-10-094643_sample-raspi.txt
$
$ head data/*sample*.txt
==> data/cr2020-04-10-094633_sample-raspi.txt <==
data/cr2020-04-10-094633_sample-raspi.txt
sample-raspi
Core data - After   0.0 seconds | CPU:  ok | Voltage:  ok | arm freq:     ok | throttled:  no | Soft temp limit: inactive | Temp: 42.9°C | Volt:  1.3500V | Freq: 1.40GHz | Load: 34%  | [ 53%,  39%,  22%,  18%]
Core data - After   2.2 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 43.5°C | Volt:  1.2000V | Freq: 1.40GHz | Load: 40%  | [ 43%,  41%,  40%,  39%]
Core data - After   3.6 seconds | CPU: NOK | Voltage: low | arm freq:     ok | throttled: yes | Soft temp limit: inactive | Temp: 45.1°C | Volt:  1.2000V | Freq: 1.40GHz | Load:100%  | [100%, 100%, 100%, 100%]
```
<a href='#raspiinfo'>return to top</a>

---
<h2 id='raspicheck' style='color:DodgerBlue'><b>raspicheck.py</b></h2>

Simulate workload on all CPU core for Raspberry Pi.
This code is independent of platform and was also tested on windows.

**how to use**

Used in <a href="#raspi">raspi.py</a> and produces same output.
Can also be invoked in python3:
```python
rcheck = RaspiCheck(setup='', timeout=10)
rcheck.main()
Enter test setup:second test
'second test' running for  0.2 minutes
Start CPU load delayed by 5 seconds
   0. Core data - After   0.0 seconds | CPU:  ok (...)
```
<a href='#raspiinfo'>return to top</a>

---

<h2 id='raspiload' style='color:DodgerBlue'><b>raspiload.py</b></h2>

Simulate workload on all CPU cores for Raspberry Pi.
Code is independent of platform and was tested Rasbian and on Windows.

- Increases CPU load to specific level
- Uses up to all cores of multi-core processors
- function to simulate load can be defined

**how to use**

in python

```python
    from raspiload import load_cpus
    timeout = 5   # runtime in seconds - effective time is longe due to overhead
    loadpct = 0.6 # approx. 60% load of CPU
    max_cpus = 2  # use only up to 2 CPUs  (None for all CPUs)
    delay = 0     # start loading after 0 seconds
    context = dict(timeout=timeout, loadpct=loadpct,
                   max_cpus=max_cpus, delay=delay)
    load_cpus(**context)
```

sample output
```console
Start test for 5 seconds on 2 CPUs with 60% load
Load CPUs terminated after 5.12 sec
```
<a href='#raspiinfo'>return to top</a>

---

<h2 id='id' style='color:DodgerBlue'><b>id.py</b></h2>

Identify your Raspberry and show all key information on screen. Save the same information in file `id.txt` .

**how to use**

from commandline: `$ python3 id.py`

or add to crontab to run at startup
```bash
# m h  dom mon dow   command
@reboot python3.7 id.py
```
**sample output**

```
 $ python3 id.py
---------------------------- Welcome to 'raspi41GB' ----------------------------
Computer Model     : Raspberry Pi 4 Model B 1gigabytes
Total memory       : 1GB
Disk Space         : total=12GB used= 68% free=4GB
Model              : Raspberry Pi 4 Model B Rev 1.1
Processorname      : ARMv7 Processor rev 3 (v7l) 7.3
Hardware - Revision: BCM2835 - a03111
# of CPUs          : - [4]
CPU frequency      : 1,500Mhz
BogoMIPs/CPU       : 270.00
CPU serial         : 100000003408c4cb
System             : Linux#1294 SMP Thu Jan 30 13:21:14 GMT 2020
Machine            : armv7l
Processor          : 
Pretty Name        : Raspbian GNU/Linux 10 (buster)"
Home URL           : http://www.raspbian.org/"
Support URL        : http://www.raspbian.org/RaspbianForums"
Platform           : linux 10.3
Python version     : 3.7.3 (default, Dec 20 2019, 18:57:59)  [GCC 8.3.0]
Active Connections
- lo               : 127.0.0.1
- eth0             : 192.168.0.235
------------------- id.py 0.1.4 -- Fri Apr 10 17:24:52 2020 --------------------
```

<a href='#raspiinfo'>return to top</a>

---
<h2 id='vpy' style='color:DodgerBlue'><b>v.py</b></h2>

Helps keeping track of version on different computer. Looks for `version`
keyword in text files and for a version number of format `0.0.1`.
Shows all text files with version numbers.

**how to use**

From commandline: `$ python3 v.py`

Specific file types are excluded in the source code:
 `exclude_ftypes = ['.sample', '.log', '.cache']`

**Sample output**
```
>---------------------------------- .gitignore ------------------------------
0.0.1     : .gitignore
------------------------------------- .md -----------------------------------
 Missing   : README.md
------------------------------------ .txt -----------------------------------
Missing   : v_sample.txt
------------------------------------- .py -----------------------------------
0.0.2     : raspi.py
0.0.14    : raspicheck.py
0.0.6     : raspiload.py
Missing   : showfonts.py
1.0.16    : v.py
-----------------------------------------------------------------------------
```
<a href='#raspiinfo'>return to top</a>

---
<h2 id='showfonts' style='color:DodgerBlue'><b>showfonts.py</b></h2>

Find all TrueType fonts ("TTF") installed on your Raspberry.
TTF can be used for example in python :
```python
from PIL import ImageFont<br>
ImageFont.truetype('Vera')
```


**how to use**

From commandline: `$ python3 showfonts.py`

<a href='#raspiinfo'>return to top</a>

---

