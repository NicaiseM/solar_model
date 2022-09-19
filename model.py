#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Future
# from __future__ import

# Standard Library
from copy import deepcopy

# Third-party Libraries

# Own sources
import epw
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Model():

    def __init__(self):
        self.opener = Opener()

    def processing(self, file, file_type):
        if file_type == 'electrical_power':
            self.el_power = self.opener.open(file, 'power')
            self.electrical_power_calc()
        elif file_type == 'heat_power':
            self.he_power = self.opener.open(file, 'power')
            # self.heat_power_calc()
        elif file_type == 'weather':
            self.weather = self.opener.open(file, 'weather')

    def electrical_power_calc(self):
        self.el_power_total = self.el_power.iloc[:, 1:].sum()
        per_cat = {
            'Datetime': self.el_power.iloc[:, 0],
            'Ligths': self.el_power.iloc[:, [1, 2]].sum(axis=1),
            'Equipment': self.el_power.iloc[:, [3, 4]].sum(axis=1),
            'Fan': self.el_power.iloc[:, [5, 6, 7, 10]].sum(axis=1),
            'Cooling': self.el_power.iloc[:, [8, 9]].sum(axis=1),
            'Pump': self.el_power.iloc[:, [10]].sum(axis=1)
            }
        self.el_power_per_cat = pd.DataFrame.from_dict(per_cat)
        self.el_power_per_cat_total = self.el_power_per_cat.iloc[:, 1:].sum()
        self.el_power_per_cat_month = self.el_power_per_cat.groupby(
            pd.Grouper(key='Datetime', freq='1M')).sum().reset_index()
        self.el_power_total_per_cat_month = \
            self.el_power_per_cat_month.sum(axis=1)

        dates = self.el_power_per_cat_month['Datetime'].dt.strftime('%b')
        cols = self.el_power_per_cat_month.shape[1] - 1
        pos = np.arange(len(dates))
        for i in range(cols):
            shift = -0.4 + i*1/cols
            plt.bar(pos + shift,
                    self.el_power_per_cat_month.iloc[:, i + 1]/1e3,
                    label=self.el_power_per_cat_month.columns[i + 1],
                    width=0.8/cols)
            plt.yscale('log')
        else:
            plt.plot(dates,
                     self.el_power_total_per_cat_month/1e3,
                     label='Total')
            plt.legend(loc='best')
            plt.grid()
            plt.ylabel('P, кВт')
            plt.yscale('log')
            plt.show()


class Opener():

    def __init__(self):
        pass

    def open(self, file, file_type):
        if file_type == 'power':
            self.power_file_open(file)
            return deepcopy(self.power)
        elif file_type == 'weather':
            self.weather_file_open(file)
            return deepcopy(self.weather)

    def power_file_open(self, file):
        with open(file, 'r') as f:
            self.power = pd.read_csv(f)
        self.power_date_convert()

    def weather_file_open(self, file):
        raw_weather = epw.epw()
        raw_weather.read(file)
        self.headers = raw_weather.headers
        self.weather = raw_weather.dataframe
        self.weather_date_convert()

    def power_date_convert(self):
        power_dt = self.power['Time']
        power_dt = pd.to_datetime(power_dt, format='%d %b %H:%M',
                                  errors='coerce').rename('Datetime')
        self.power = pd.concat((power_dt, self.power.iloc[:, 1:]),
                               axis=1).dropna().sort_values('Datetime')
        self.power = self.power.reset_index(drop=True)

    def weather_date_convert(self):
        weather_dt = self.weather.loc[:, 'Year':'Hour']
        weather_dt.loc[:, 'Hour'] = weather_dt.loc[:, 'Hour'] - 1
        weather_dt = pd.to_datetime(weather_dt)
        weather_dt = weather_dt.map(lambda x: x.replace(year=1900))
        weather_dt = weather_dt.rename('Datetime')
        self.weather = pd.concat((weather_dt, self.weather.iloc[:, 6:]),
                                 axis=1)
        self.weather = self.weather.groupby(['Datetime'], as_index=False)
        self.weather = self.weather.mean().sort_values('Datetime')
        self.weather = self.weather.reset_index(drop=True)


if __name__ == '__main__':

    model = Model()
    electrical_power_file = r'./raw_data/my_home_electricity.csv'
    heat_power_file = r'./raw_data/my_home_heat.csv'
    weather_file = r'./raw_data/RUS_Arkhangelsk.225500_IWEC.epw'

    model.processing(electrical_power_file, 'electrical_power')
    model.processing(heat_power_file, 'heat_power')
    model.processing(weather_file, 'weather')
