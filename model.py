#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Future
# from __future__ import

# Standard Library
import locale
from copy import deepcopy

# Third-party Libraries

# Own sources
import epw
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


# === Классы ===
class Model():
    """Класс - обработчик данных."""

    def __init__(self):
        """
        Конструктор объекта.

        Returns
        -------
        None.

        Notes
        -----
        При создании объекта класса Model в нем создается вложенный
        объект класса Opener, кроме того, определяются словарь для
        хранения таблиц мощности (#0 - электрическая, #1 - тепловая)
        и поле для таблицы дынных погодных условий.

        """
        self.opener = Opener()  # Создание объекта для открытия .epw и .csv
        self.power = [None, None]
        self.weather = None

    def processing(self, file, file_type, show_tables=False, show_plot=True):
        """
        Внешний метод обработки данных.

        Parameters
        ----------
        file : PathLike
            Обрабатываемый файл.
        file_type : str
            Параметр, указывающий на тип файла.
        show_tables : bool, default False
            Флаг вывода таблиц.
        show_plot : bool, default True
            Флаг вывода таблиц.

        Returns
        -------
        None.

        Notes
        -----
        Метод, в зависимости от переданного строкового параметра
        типа, извлекает данные из файла посредством метода open
        вложенного объекта opener и передает их на обработку
        соответствующему методу.

        """
        # Если файл содержит информацию о, энергопотреблении
        if file_type == 'electrical_power' or file_type == 'heat_power':
            # Извлечение в соответствующий элемент в зависимости от типа
            if file_type == 'electrical_power':
                self.power[0] = [self.opener.open(file, 'csv')]
            else:
                self.power[1] = [self.opener.open(file, 'csv')]
            self.power_calc(file_type, show_tables)  # Обработка данных
        # Если файл содержит сведения о погоде
        elif file_type == 'weather':
            self.weather = self.opener.open(file, 'epw')  # Открытие файла
        else:
            print('Тип файла не поддерживается.')

    def power_calc(self, file_type, show_tables=False, show_plot=True):
        """
        Обработка данных энергопотребления.

        Parameters
        ----------л.
        file_type : str
            Параметр, указывающий на тип файла.
        show_tables : bool, default False
            Флаг вывода таблиц.
        show_plot : bool, default True
            Флаг вывода таблиц.

        Returns
        -------
        None.

        Notes
        -----
        Метод определяет суммарные значения по каждому столбцу таблицы
        энергопотребления и вписывает их последней строкой

        """
        # Назначение элемента списка power для размещения
        # значений в зависимости от типа файла
        if file_type == 'electrical_power':
            power = self.power[0]
        else:
            power = self.power[1]
        power_total_per_time = power[0].iloc[:, 1:].sum(axis=1).rename('Total')
        power[0] = pd.concat((power[0], power_total_per_time), axis=1)
        # Определение суммарных значений
        power_total = power[0].iloc[:, 1:].sum()
        # Создание заголовка строки суммарных значений
        total_dt = pd.Series(['Total'], index=['Datetime'])
        # Формирование строки из заголовка и суммарных значений
        power_total = pd.concat((total_dt, power_total)).to_frame().T
        # Добавление строки суммарных значений в конец таблицы
        power[0] = pd.concat((power[0], power_total)).reset_index(drop=True)
        # Получение словаря категорий
        cat = self.assign_categories(power, file_type)
        # Запись таблицы энергопотребления в соответствующий элемент
        power.append(pd.DataFrame.from_dict(cat))
        # Создание группировки по месяцам
        power.append(power[1].iloc[:-1, :].groupby(
            pd.Grouper(key='Datetime', freq='1M')).sum().reset_index())
        # Суммирование по месяцам и запись в соответствующий элемент
        # power.append(power_per_cat_per_month.sum(axis=1))
        power[2] = pd.concat((power[2], power[1].iloc[-1, :].to_frame().T))
        power[2] = power[2].reset_index(drop=True)
        # Печать таблиц при необходимости
        if show_tables:
            self.print_tables(power)
        if show_plot:
            self.power_plot(power)

    def assign_categories(self, power, file_type):
        if file_type == 'electrical_power':
            cat = {
                'Datetime': power[0].iloc[:, 0],
                'Ligths': power[0].iloc[:, [1, 2]].sum(axis=1),
                'Equipment': power[0].iloc[:, [3, 4]].sum(axis=1),
                'Fan': power[0].iloc[:, [5, 6, 7, 10]].sum(axis=1),
                'Cooling': power[0].iloc[:, [8, 9]].sum(axis=1),
                'Pump': power[0].iloc[:, [10]].sum(axis=1),
                'Total': power[0].iloc[:, [11]].sum(axis=1)
                }
        else:
            cat = {
                'Datetime': power[0].iloc[:, 0],
                'Heating': power[0].iloc[:, [1, 2]].sum(axis=1),
                'Cooling': power[0].iloc[:, [3, 4, 5]].sum(axis=1),
                'Total': power[0].iloc[:, [6]].sum(axis=1)
                }
        return cat

    def print_tables(self, power):
        print('Энергопотребление')
        print(50*'-' + '\nИсходная таблица')
        print(power[0])
        print(50*'-' + '\nТаблица по категориям')
        print(power[1])
        print(50*'-' + '\nТаблица по категориям по месяцам')
        print(power[2])

    def power_plot(self, power):
        # dates = self.el_power_per_cat_month['Datetime'].dt.strftime('%b')
        # cols = self.el_power_per_cat_month.shape[1] - 1
        # pos = np.arange(len(dates))
        # for i in range(cols):
        #     shift = -0.4 + i*1/cols
        #     plt.bar(pos + shift,
        #             self.el_power_per_cat_month.iloc[:, i + 1]/1e3,
        #             label=self.el_power_per_cat_month.columns[i + 1],
        #             width=0.8/cols)
        #     plt.yscale('log')
        # else:
        #     plt.plot(dates,
        #              self.el_power_total_per_cat_month/1e3,
        #              label='Total')
        #     plt.legend(loc='best')
        #     plt.grid()
        #     plt.ylabel('P, кВт')
        #     plt.yscale('log')
        #     plt.show()
        pass

class Opener():
    """Класс - экстрактор данных из .epw и .csv."""

    def __init__(self):
        pass

    def open(self, file, file_type):
        """
        Метод открытия файла способом, соответствующим его типу.

        Parameters
        ----------
        file : PathLike
            Обрабатываемый файл.
        file_type : str
            Параметр, указывающий на тип файла.

        Returns
        -------
        self.power : DataFrame
            Данные энергопотребления.
        or
        self.weather : DataFrame
            Данные погодного файла.

        Notes
        -----
        Метод, в зависимости от переданного строкового параметра
        типа, перенаправляет файл соответствующему методу на
        извлечение данных.
        """
        if file_type == 'csv':  # Если файл - .csv
            self.power_file_open(file)  # Извлечение данных
            return deepcopy(self.power)  # Возврат копии полученных данных
        elif file_type == 'epw':  # Если файл - .epw
            self.weather_file_open(file)  # Извлечение данных
            return deepcopy(self.weather)  # Возврат копии полученных данных

    def power_file_open(self, file):
        """
        Открытие csv-файла энергопотребления.

        Parameters
        ----------
        file : PathLike
            Обрабатываемый файл.

        Returns
        -------
        None.

        Notes
        -----
        Метод извлекает данные из файла и отправляет на конвертацию.
        """
        with open(file, 'r') as f:  # Открытие файла
            self.power = pd.read_csv(f)  # Считывание данных
        self.power_date_convert()  # Конвертация дат в pd.Timestamp

    def weather_file_open(self, file):
        """
        Открытие epw-файла погодных условий.

        Parameters
        ----------
        file : PathLike
            Обрабатываемый файл.

        Returns
        -------
        None.

        Notes
        -----
        Метод, в зависимости от переданного строкового параметра
        типа, перенаправляет файл соответствующему методу на
        извлечение данных.

        Notes
        -----
        Метод извлекает данные из файла и отправляет на конвертацию.
        """
        raw_weather = epw.epw()  # Создание объекта epw
        raw_weather.read(file)  # Считывание данных
        self.weather = raw_weather.dataframe  # Конвертация данных в DataFrame
        # Конвертация дат в pd.Timestamp, усреднение данных по годам
        self.weather_date_convert()

    def power_date_convert(self):
        """
        Приведение извлеченных данных энергопотребления в нужный вид.

        Returns
        -------
        None.

        Notes
        -----
        Метод извлекает столбец времени из считанных данных, приводит
        его в формат pd.Timestamp, после чего объединяет с исходным
        массивом данных и производит сортировку по времени.

        """
        power_dt = self.power['Time']  # Извлечение столбца времени
        # Приведение времени в формат pd.Timestamp
        power_dt = pd.to_datetime(power_dt, format='%d %b %H:%M',
                                  errors='coerce').rename('Datetime')
        # Объединение массивов, сортировка по времени
        self.power = pd.concat((power_dt, self.power.iloc[:, 1:]),
                               axis=1).dropna().sort_values('Datetime')
        # Сброс индексации после сортировки
        self.power = self.power.reset_index(drop=True)

    def weather_date_convert(self):
        """
        Приведение извлеченных данных из погодного файла в нужный вид.

        Returns
        -------
        None.

        Notes
        -----
        Метод извлекает столбец времени из считанных данных, приводит
        его в формат pd.Timestamp, после чего объединяет с исходным
        массивом данных и производит сортировку по времени. Сортировка
        производится усреднением одинаковых дат, поэтому предварительно
        все значения годов проставляются равными 1900.

        """
        # Извлечение таблицы с информацией о времени
        weather_dt = self.weather.loc[:, 'Year':'Hour']
        # Уменьшение значений часов на 1 (в исходном файле вместо
        # 00:00 указывается 24:00 и год начинается с 01.01 01:00)
        weather_dt.loc[:, 'Hour'] = weather_dt.loc[:, 'Hour'] - 1
        # Приведение таблицы времени в вектор объектов pd.Timestamp
        weather_dt = pd.to_datetime(weather_dt)
        # Замена всех значений годов на 1900 (для усреднения)
        weather_dt = weather_dt.map(lambda x: x.replace(year=1900))
        # Переименование столбца времени
        weather_dt = weather_dt.rename('Datetime')
        # Объединение массивов
        self.weather = pd.concat((weather_dt, self.weather.iloc[:, 6:]),
                                 axis=1)
        # Группировка значений с одинаковыми датами
        self.weather = self.weather.groupby(['Datetime'], as_index=False)
        # Усреднение данных по годам, сортировка по времени
        self.weather = self.weather.mean().sort_values('Datetime')
        # Сброс индексации после сортировки
        self.weather = self.weather.reset_index(drop=True)

# === Функции ===


# === Обработка ===
# Смена локали на английскую (для корректной работы на Unix-системах)
locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
# Задание размеров выходных графиков
mpl.rcParams['figure.figsize'] = [8.0, 6.0]

if __name__ == '__main__':

    model = Model()
    electrical_power_file = r'./raw_data/my_home_electricity.csv'
    heat_power_file = r'./raw_data/my_home_heat.csv'
    weather_file = r'./raw_data/RUS_Arkhangelsk.225500_IWEC.epw'

    model.processing(electrical_power_file,
                      'electrical_power',
                      show_tables=True)
    model.processing(heat_power_file,
                      'heat_power',
                      show_tables=True)
    # model.processing(weather_file, 'weather')
