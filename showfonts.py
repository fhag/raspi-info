# -*- coding: utf-8 -*-
'''
List all available truetype fonts in your raspberry
@author: GFI

requires Python 3.6 or later
'''
import os

__version__ = '0.0.1'


PATH = '/usr/share/fonts/truetype'

if __name__ == '__main__':
    print(os.listdir(PATH))
    for folder in os.walk(PATH):
        print(folder[0])
        for i, font in enumerate(folder[2]):
            if 'ttf' in font:
                print(f'{i:4.0f}.   {font}')
