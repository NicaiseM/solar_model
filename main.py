#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Future
# from __future__ import

# Standard Library
import sys

# Third-party Libraries

# Own sources
import model

__author__      = "Nikita Makarchuk"
__copyright__   = "Copyright 2022, Nikita Makarchuk"
__credits__     = ["Nikita Makarchuk"]
__license__     = "GPL"
__version__     = "0.3.1"
__maintainer__  = "Nikita Makarchuk"
__email__       = "nicaise@rambler.ru"
__status__      = "Development"


# === Классы ===

# === Функции ===

# === Обработка ===
if __name__ == '__main__':

    model = model.Model()
    electrical_power_file = r'./raw_data/my_home_electricity.csv'
    heat_power_file = r'./raw_data/my_home_heat.csv'
    weather_file = r'./raw_data/RUS_Arkhangelsk.225500_IWEC.epw'

    if sys.argv[1] == 'electrical_power':
        model.processing(electrical_power_file, 'electrical_power')
    elif sys.argv[1] == 'heat_power':
        model.processing(heat_power_file, 'heat_power')
    elif sys.argv[1] == 'weathe':
        model.processing(weather_file, 'weather')
