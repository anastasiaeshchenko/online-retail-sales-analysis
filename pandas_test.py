import pandas as pd
import matplotlib.pyplot as plt

# загрузка данных

df = pd.read_excel('Online_Retail.xlsx')

# подготовка данных

sales = df[
    ((df['Quantity'] > 0) | ((df['Quantity'] <0) & (df['InvoiceNo'].astype(str).str.startswith('C'))))
    & (df['UnitPrice'] >= 0)
]

sales = sales.drop_duplicates().copy()
sales['Revenue'] = sales['Quantity'] * sales['UnitPrice']
sales['Month'] = sales['InvoiceDate'].dt.to_period('M')

# анализ выручки
revenue = sales['Revenue'].sum()
revenue_month = sales.groupby('Month')['Revenue'].sum()
print('Общая выручка:', round(revenue, 2))

# анализ товаров и стран

product_sales = sales[~sales['StockCode'].isin(['DOT', 'POST'])]
products = product_sales.groupby('StockCode')['Revenue'].sum()
top_codes =  products.nlargest(10).index
name_counts = (
    product_sales[product_sales['StockCode'].isin(top_codes)]
    .groupby(['StockCode', 'Description'])
    .size())
best_names = (
    name_counts.reset_index(name='Count')
    .sort_values('Count', ascending=False)
    .drop_duplicates(subset='StockCode'))
top10 = (products.nlargest(10).reset_index().merge(
    best_names[['StockCode', 'Description']], on='StockCode', how ='left', validate='one_to_one'
))

print('\nТоп-10 товаров по выручке:')
print(top10)

countries = sales.groupby('Country')['Revenue'].sum()
top_countries = countries.nlargest(10)
country_share = countries / revenue * 100
print('\nТоп-10 стран по доле выручки (%):')
print(country_share.nlargest(10).round(2))

# анализ покупателей

unique_buyer = sales['CustomerID'].nunique()
print('Количество покупателей:', unique_buyer)

# анализ заказов

revenue_order = sales[sales['Quantity'] > 0].groupby('InvoiceNo')['Revenue'].sum()
revenue_order_mean = revenue_order.mean()
print('Средний чек:', revenue_order_mean.round(2))
print('Медианный чек:', revenue_order.median().round(2))
large_orders = (revenue_order > 1000).sum()
print('Доля заказов дороже 1000 (%):',
      round(large_orders / len(revenue_order) * 100, 2))
customer_orders = sales[(sales['Quantity'] > 0) & (sales['CustomerID'].notna())]
orders = customer_orders.groupby('CustomerID')['InvoiceNo'].nunique()
purch = (orders >= 2).sum()
print('Доля повторных покупателей (%):',
      round(purch / len(orders) * 100, 2))
print('Среднее количество заказов на покупателя:',
      round(orders.mean(), 2))

# визуализация данных
revenue_month.plot(kind='line')
plt.title('Monthly Revenue')
plt.xlabel('Month')
plt.ylabel('Revenue')
plt.grid(True)
plt.tight_layout()
plt.savefig('monthly_revenue.png', dpi=300, bbox_inches='tight')
plt.close()

top10.plot(kind='barh', x='Description', y='Revenue', figsize=(12,6))
plt.title('Top 10 Products by Revenue')
plt.xlabel('Revenue')
plt.ylabel('Product')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('top10_products.png', dpi=300, bbox_inches='tight')
plt.close()

top_countries.plot(kind='bar', figsize=(12,6))
plt.title('Top 10 Countries by Revenue')
plt.xlabel('Countries')
plt.ylabel('Revenue')
plt.tight_layout()
plt.savefig('top10_countries.png', dpi=300, bbox_inches='tight')
plt.close()
