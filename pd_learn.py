import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Работа с временем

# month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              # 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

a = pd.Series(['01 Jan 08:00', '01 Jan 09:00', '01 Jan 10:00'])
a = pd.to_datetime(a, format='%d %b %H:%M')

b = pd.Series(['2000 01 Jan 08:00', '2000 01 Jan 09:00', '2000 01 Jan 10:00',
               '2001 01 Jan 08:00', '2001 01 Jan 09:00', '2001 01 Jan 10:00',
               '2001 01 Aug 08:00'])
b = pd.to_datetime(b, format='%Y %d %b %H:%M')
data = pd.Series([1, 2, 3, 4, 5, 6, 7])
df = {'Datetime': b, 'Data': data}
df = pd.DataFrame(df)
dt = df['Datetime'].map(lambda x: x.replace(year=1900)).rename('Datetime')
df = pd.concat((dt, df.iloc[:, 1:]), axis=1)
df = df.groupby(['Datetime'], as_index=False).mean()
df_month_sum = df.groupby(pd.Grouper(key='Datetime',
                                     freq='1M')).sum().reset_index()

dates = df_month_sum['Datetime'].dt.strftime('%b')
plt.plot(dates, df_month_sum['Data'])

def printt(file):
    with open(file, 'r') as f:
        string = f.read()
        print(string)

