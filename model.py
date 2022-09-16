# -*- coding: utf-8 -*-

import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from epw import epw

class Model():
    
    def __init__(self):
        self.month = {'Jan': 1,
                      'Feb': 2,
                      'Mar': 3,
                      'Apr': 4,
                      'May': 5,
                      'Jun': 6,
                      'Jul': 7,
                      'Aug': 8,
                      'Sep': 9,
                      'Oct': 10,
                      'Nov': 11,
                      'Dec': 12}

    def processing(self, power_file, weather_file):
        self.open(power_file, weather_file)
        # self.power_date_convert()
        self.weather_date_convert()
        self.weather_averaging()

    def open(self, power_file, weather_file):
        with open(power_file, 'r') as f:
            self.power = pd.read_csv(f)
        raw_weather = epw()
        raw_weather.read(weather_file)
        self.headers = raw_weather.headers
        self.weather = raw_weather.dataframe

    def power_date_convert(self):
        date = ['Year', 'Month', 'Day', 'Hour', 'Minute']
        power_dt = pd.DataFrame(columns=date)
        tmp_dt = self.power.loc[:, 'Time']
        for i in range(len(tmp_dt)):
            list_dt = tmp_dt.loc[i].split()
            month = self.month[list_dt[1]]
            day = list_dt[0]
            hour = list_dt[2].split(':')[0]
            minute = list_dt[2].split(':')[1]
            next_row = [0, month, day, hour, minute]
            next_row = [[int(i) for i in next_row]]
            next_row = pd.DataFrame(next_row,
                                    columns=date)
            power_dt = pd.concat((power_dt, next_row),
                                 ignore_index=True)
        power_dt = pd.to_datetime(power_dt).rename('Datetime')
        first_col = self.power.columns[1]
        self.power = pd.concat((power_dt, self.power.loc[:, first_col:]),
                               axis=1).sort_values('Datetime')
        self.power = self.power.reset_index(drop=True)

    def weather_date_convert(self):
        weather_dt = self.weather.loc[:, 'Year':'Hour']
        weather_dt.loc[:, 'Hour'] = weather_dt.loc[:, 'Hour'] - 1
        weather_dt = pd.to_datetime(weather_dt).rename('Datetime')
        first_col = self.weather.columns[6]
        self.weather = pd.concat((weather_dt, self.weather.loc[:, first_col:]),
                                 axis=1).sort_values('Datetime')
        self.weather = self.weather.reset_index(drop=True)

    def year_to_zero(self, df):
        datetime = pd.Series([]).rename.('Datetime')
        tmp_datetime = df.Datetime
        for i in range(len(tmp_datetime)):
            dt = tmp_datetime.loc[i].replace(year=0)
            datetime = pd.concat((datetime, dt),
                                 ignore_index=True)

    def weather_averaging(self):
        years = self.weather.Datetime.dt.year.drop_duplicates()
        years = years.reset_index(drop=True)
        for year in years:
            y_weather = self.weather[self.weather.Datetime.dt.year == 1982]
            y_weather = y_weather.reset_index(drop=True)
            if hasattr(self, 'average_weather'):
                pass
            else:
                
                for in range in 
                tmp_datetime = y_weather.Datetime.dt.replace(year=0)
                pass
        

# pd.to_datetime(power.loc[1, 'Time'])

# time = power.loc[1, 'Time']

model = Model()
model.processing('my_home.csv', r'RUS_Arkhangelsk.225500_IWEC.epw')