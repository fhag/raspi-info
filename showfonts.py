# -*- coding: utf-8 -*-
'''
List all available truetype fonts in your raspberry
@author: GFI

requires Python 3.6 or later
'''
import os

path = '/usr/share/fonts/truetype'

if __name__ == '__main__':
    print(os.listdir(path))
    for folder in os.walk(path):
        print(folder[0])
        for i, font in enumerate(folder[2]):
            if 'ttf' in font:
                print(f'{i:4.0f}.   {font}')
