# -*- coding: utf-8 -*-

import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from epw import epw

class Model():
    
    def __init__(self):
        pass

    def processing(self, power_file, weather_file):
        self.open(power_file, weather_file)
        self.power_date_convert()
        self.weather_date_convert()
        self.power_calc()

    def open(self, power_file, weather_file):
        with open(power_file, 'r') as f:
            self.power = pd.read_csv(f)
        raw_weather = epw()
        raw_weather.read(weather_file)
        self.headers = raw_weather.headers
        self.weather = raw_weather.dataframe

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

    def power_calc(self):
        self.power_total = self.power.iloc[:, 1:].sum()
        per_cat = {
            'Datetime': self.power.iloc[:, 0],
            'Ligths': self.power.iloc[:, [1, 2]].sum(axis=1),
            'Equipment': self.power.iloc[:, [3, 4]].sum(axis=1),
            'Fan': self.power.iloc[:, [5, 6, 7, 10]].sum(axis=1),
            'Cooling': self.power.iloc[:, [8, 9]].sum(axis=1),
            'Pump': self.power.iloc[:, [10]].sum(axis=1)
            }
        self.power_per_cat = pd.DataFrame.from_dict(per_cat)
        self.power_per_cat_total = self.power_per_cat.iloc[:, 1:].sum()
        self.power_per_cat_month = self.power_per_cat.groupby(
            pd.Grouper(key='Datetime',
            freq='1M')).sum().reset_index()
        self.power_total_per_cat_month = self.power_per_cat_month.sum(axis=1)
 
        dates = self.power_per_cat_month['Datetime'].dt.strftime('%b')
        cols = self.power_per_cat_month.shape[1] - 1
        pos = np.arange(len(dates))
        for i in range(cols):
            shift = -0.4 + i*1/cols
            plt.bar(pos + shift,
                    self.power_per_cat_month.iloc[:, i + 1]/1e3,
                    label=self.power_per_cat_month.columns[i + 1],
                    width=0.8/cols)
            plt.yscale('log')
        else:
            plt.plot(dates, self.power_total_per_cat_month/1e3, label='Total')
            plt.legend(loc='best')
            plt.grid()
            plt.ylabel('P, кВт')
            plt.yscale('log')
            plt.show()



model = Model()
model.processing('my_home.csv', r'RUS_Arkhangelsk.225500_IWEC.epw')