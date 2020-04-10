# raspi-info
Some utilies to collect information about your Raspberry and 
monitor CPU status.

**Table of Contents**

[TOCM]

---
<dl>
  <dt>Definition list</dt>
  <dd>Is something people use sometimes.</dd>

  <dt>Markdown in HTML</dt>
  <dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>
</dl>
---

## raspi.py

---

## raspicheck.py

**Usage**

**Features**

**Sample Output**

<br>


---

## raspiload.py


**Usage**

**Features**
- Increases CPU load to specific level
- Function

-- load_single_cpu(timeout=5, load_pct=1.00, load_func=None, fname='')

Keywords parameters
>timeout=5  # time in seconds to apply load on CPU

>load_pct=1.00  # aproximate load to apply on CPUs

>load_func=None

    def _load_func():
        '''Function to load cpu'''
        _ = math.log(random.random())


>fname=''

**Sample**


<br>


---
## showfonts.py

**Usage**

Find all TrueType fonts (TTF) installed on your Raspberry.
TTF can be used for example in python :

>from PIL import ImageFont<br>
>ImageFont.truetype('Vera')

<br>

---
## v.py

**usage**

 > ~raspi-info $ python3 v.py
  
**Features**
- Helps keeping track of version on different computer
- Shows all text files including with version numbers

Specific file types can be excluded in the source code

>exclude_ftypes = ['.sample', '.log', '.cache']

**Sample output**

>---------------------------------- .gitignore ------------------------------
<br>0.0.1     : .gitignore
<br>------------------------------------- .md ---------------------------------
<br> Missing   : README.md
<br>------------------------------------- .txt ---------------------------------
<br> Missing   : v_sample.txt
<br>------------------------------------- .py ---------------------------------
<br> 0.0.2     : raspi.py
<br> 0.0.14    : raspicheck.py
<br> 0.0.6     : raspiload.py
<br> Missing   : showfonts.py
<br> 1.0.16    : v.py
<br>---------------------------------------------------------------------------

---