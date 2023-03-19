# -*- coding: utf-8 -*-
"""
@author: User
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime

df = pd.read_csv('C:/Users/User/OneDrive/桌面/python_RFM/RFM_202106-202204.csv')
df.head()



#check order status
df['order_status'].unique()

#take off fail order
df = df.loc[df['order_status'] == 'completed', :]
print ('completed', len(df))

#check missing value
df.info()
df.isnull().sum()



#create recency#
recency_df = df.groupby('user_id')['order_date'].max().reset_index()
recency_df

now = datetime.date.today()

recency_df['recency'] = (pd.to_datetime(now) - pd.to_datetime(recency_df['order_date'])).dt.days
recency_df

#recency EDA
plt.hist(recency_df.recency)
plt.show()

plt.boxplot(recency_df.recency)
plt.show()

pd.DataFrame(recency_df['recency'].describe())



#create frequency#
df['date_tag'] = df['order_date'].astype(str)

dd_frequency = df.groupby(['user_id', 'date_tag'])['order_date'].count().reset_index()
dd_frequency

frequency_df = dd_frequency.groupby('user_id')['order_date'].count().reset_index()
frequency_df = frequency_df.rename(columns = {'user_id':'user_id', 'order_date':'frequency'})
frequency_df.info()

#frequency EDA
x = frequency_df.frequency.value_counts()

plt.pie(x, autopct='%1.1f%%')
plt.show()



#create monetary#
monetary_df1 = df.groupby('order_id')['revenue'].max().reset_index()
monetary_df1

monetary_df2 = monetary_df1.merge(df, on = ('order_id'), how='left')
monetary_df2
monetary_df2.columns
monetary_df2.info()


monetary_df = monetary_df2.groupby('user_id')['revenue_x'].sum().reset_index()
monetary_df

monetary_df = monetary_df.rename(columns = {'user_id':'user_id', 'revenue_x':'monetary_sum'})
monetary_df

#monetary EDA
plt.hist(monetary_df.monetary_sum)
plt.show()

plt.boxplot(monetary_df.monetary_sum)
plt.show()

pd.DataFrame(monetary_df['monetary_sum'].describe())



#RFM合併
df1 = pd.merge(monetary_df, frequency_df, right_on='user_id', left_on='user_id')
df1.head()

df1['monetary'] = round(df1['monetary_sum'] / df1['frequency'])

new_df = pd.merge(df1, recency_df, right_on='user_id', left_on='user_id')
new_df = new_df[['user_id', 'recency', 'frequency', 'monetary']]
new_df
new_df.info()


#RFM EDA#
#recency (切25%, 50% 分3群)
new_df['recency'].describe()

plt.hist(new_df.recency)
plt.show()

plt.boxplot(new_df.recency)
plt.show()

#frequency (切買1, 2, 3up 分3群)
new_df.frequency.value_counts()

plt.pie(new_df.frequency.value_counts(), autopct='%1.1f%%')
plt.show()

#monetary (切中位數 分2群)
new_df['monetary'].describe()

plt.hist(new_df.monetary)
plt.show()

plt.boxplot(new_df.monetary)
plt.show()



###切割###

#cut Recency
new_df['recency_level'] = pd.cut(new_df['recency'], bins=[0, 60, 120, 1000], labels=[3, 2, 1], right=False).astype(float)

#cut Frequency
new_df['frequency_level'] = pd.cut(new_df['frequency'], bins=[1,2,3,100], labels=[1, 2, 3], right=False).astype(float)

#cut Monetary
new_df['monetary_level'] = pd.cut(new_df['monetary'], bins=[0, 1055, 100000], labels=[1, 2], right=False).astype(float)

print(new_df)

#count
new_df.recency_level.value_counts()
new_df.frequency_level.value_counts()
new_df.monetary_level.value_counts()


#(r,f,m)
new_df['RFM_level'] = (new_df['recency_level']*100 + new_df['frequency_level']*10 + new_df['monetary_level']).astype(int)

new_df.head()
new_df.RFM_level.value_counts()

#done
new_df.to_csv('Care+_RFM_Model_Result.csv', encoding='utf_8_sig')