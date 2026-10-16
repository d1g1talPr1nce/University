import numpy 
import matplotlib.pyplot as plt 
import pandas as pd

#Najděte korelační koeficient mezi prodeji v NA a EU

plt.style.use('dark_background')

df = pd.read_csv('vgsales.csv')
df_eu_sales = df['EU_Sales']
df_na_sales = df['NA_Sales']

korelace = df_eu_sales.corr(df_na_sales)
print(f"Korelační faktor je: {korelace:.6f}")

df_obodi_1985_2010 = df[(df['Year'] >= 1985) & (df['Year'] <= 2010)]

korelace_rozdelene = df_obodi_1985_2010.groupby('Year').apply(lambda x : x['NA_Sales'].corr(x['EU_Sales'])).plot(style='o', color = '#00ffcc')

plt.title('Korelace mezi jednotlivými roky (1985-2010)', fontsize = 14, fontweight = 'bold')
plt.xlabel('Roky', fontsize = 12)
plt.ylabel('Korelace', fontsize = 12)
plt.grid(axis='y', alpha = 0.2)
plt.show()
